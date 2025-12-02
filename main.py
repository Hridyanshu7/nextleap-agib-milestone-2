import logging
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import requests

from app_store_review_scraper.scrapers.google_play_scraper import GooglePlayScraper
from app_store_review_scraper.scrapers.app_store_scraper import AppStoreScraper
from app_store_review_scraper.analysis.summarizer import ReviewAnalyzer
from app_store_review_scraper.notifications.email_sender import EmailSender
from app_store_review_scraper.models.base import init_db, SessionLocal
from app_store_review_scraper.models.review import Review, ReviewSource, ReviewSentiment
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def save_reviews_to_db(df: pd.DataFrame, app_id: str):
    """Save reviews to database, avoiding duplicates"""
    if df.empty:
        return
    db = SessionLocal()
    try:
        new_count = 0
        for _, row in df.iterrows():
            review_id = row.get('reviewId') or row.get('id')
            if not review_id:
                import hashlib
                unique_str = f"{row['user_name']}{row['review_date']}{row['review_text'][:20]}"
                review_id = hashlib.md5(unique_str.encode()).hexdigest()
            if db.query(Review).filter(Review.review_id == str(review_id)).first():
                continue
            review = Review(
                review_id=str(review_id),
                source=ReviewSource(row['source']),
                app_id=app_id,
                app_version=row.get('app_version'),
                user_name=row.get('user_name'),
                rating=row['rating'],
                title=row.get('title'),
                content=row['review_text'],
                review_date=row['review_date'],
                country='us',
                developer_reply=row.get('developer_reply'),
                developer_reply_date=row.get('reply_date'),
                thumbs_up=row.get('thumbs_up', 0),
                is_edited=row.get('is_edited', False)
            )
            if 'sentiment' in row:
                try:
                    review.sentiment = ReviewSentiment(row['sentiment'])
                    review.sentiment_score = row.get('sentiment_score')
                except ValueError:
                    pass
            db.add(review)
            new_count += 1
        db.commit()
        logger.info(f"Saved {new_count} new reviews to database")
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving reviews: {str(e)}")
    finally:
        db.close()

def parse_play_url(url: str):
    """Extract the package name, language, and country from a Google Play Store URL"""
    parsed = urlparse(url.strip())
    if 'play.google.com' not in parsed.netloc.lower():
        return None
    qs = parse_qs(parsed.query)
    pkg = qs.get('id', [None])[0]
    if not pkg:
        parts = parsed.path.split('/')
        if 'details' in parts:
            idx = parts.index('details') + 1
            if idx < len(parts) and parts[idx].startswith('id='):
                pkg = parts[idx][3:]
    
    # Extract language (hl) and country (gl)
    lang = qs.get('hl', ['en'])[0]
    country = qs.get('gl', ['us'])[0]
    
    # If lang is like 'en_IN', split it.
    # google-play-scraper prefers 'en' over 'en_IN' for the lang parameter, 
    # while 'in' should be passed as the country parameter.
    if '_' in lang:
        parts = lang.split('_')
        if len(parts) == 2:
            # If country (gl) wasn't explicitly set, use the region from lang
            if country == 'us' and 'gl' not in qs:
                country = parts[1].lower()
            # Strip region from lang to keep it simple (e.g. 'en')
            lang = parts[0]
            
    return {'package_name': pkg, 'lang': lang, 'country': country}

def lookup_apple_app(package_name: str, country: str = 'us'):
    """Check if an app with the given Android package exists on the Apple App Store.
    Returns a tuple (app_id, app_name) if found, otherwise (None, None).
    """
    try:
        resp = requests.get('https://itunes.apple.com/lookup', params={'bundleId': package_name, 'country': country}, timeout=10)
        data = resp.json()
        if data.get('resultCount', 0) > 0:
            result = data['results'][0]
            return str(result.get('trackId')), result.get('trackName')
    except Exception as e:
        logger.error(f"Apple lookup failed: {e}")
    return None, None

def timed_input(prompt, timeout=15, default=None):
    """
    Get user input with a timeout. Returns default if timeout occurs.
    
    Args:
        prompt (str): The input prompt to display
        timeout (int): Timeout in seconds
        default (str): Default value if timeout occurs
        
    Returns:
        str: User input or default value
    """
    import sys
    import select
    
    # For Windows compatibility
    if sys.platform == 'win32':
        import msvcrt
        import time
        
        print(prompt, end='', flush=True)
        start_time = time.time()
        input_str = ''
        
        while True:
            if msvcrt.kbhit():
                char = msvcrt.getwche()
                if char == '\r':  # Enter key
                    print()
                    return input_str if input_str else default
                elif char == '\b':  # Backspace
                    if input_str:
                        input_str = input_str[:-1]
                        # Clear the character from console
                        print('\b \b', end='', flush=True)
                else:
                    input_str += char
            
            if time.time() - start_time > timeout:
                print()
                if default:
                    logger.info(f"No input received. Using default: {default}")
                return default
            
            time.sleep(0.1)
    else:
        # Unix-like systems
        print(prompt, end='', flush=True)
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.readline().rstrip('\n')
        else:
            print()
            if default:
                logger.info(f"No input received. Using default: {default}")
            return default

def run_scraper():
    """Main execution: ask for Play Store URL, optionally scrape Apple Store if app exists"""
    logger.info("Starting review scraper...")
    init_db()
    analyzer = ReviewAnalyzer(gemini_api_key=config.GEMINI_API_KEY)
    all_reviews = []

    # Default URLs for Groww app
    default_play_url = "https://play.google.com/store/apps/details?id=com.nextbillion.groww&hl=en_IN"
    default_apple_url = "https://apps.apple.com/in/app/groww-stocks-mutual-fund-ipo/id1404871703"
    
    # Get Google Play Store URL with timeout
    play_url = timed_input(
        "Enter the Google Play Store URL of the app to scrape (5s timeout): ",
        timeout=5,
        default=default_play_url
    )
    
    if not play_url:
        play_url = default_play_url
        logger.info(f"Using default Google Play URL: {play_url}")
    
    play_url = play_url.strip()
    parsed_data = parse_play_url(play_url)
    if not parsed_data or not parsed_data['package_name']:
        logger.error("Could not parse a valid Google Play package name from the URL.")
        return
    
    package_name = parsed_data['package_name']
    lang = parsed_data['lang']
    country = parsed_data['country']
    
    logger.info(f"Detected Google Play package: {package_name}, Lang: {lang}, Country: {country}")

    gp_scraper = GooglePlayScraper(package_name, lang=lang, country=country)
    
    # Fetch the actual app name from Play Store
    app_name = gp_scraper.get_app_name()
    if not app_name:
        app_name = package_name  # Fallback to package name if fetch fails
        logger.warning(f"Could not fetch app name, using package name: {package_name}")
    else:
        logger.info(f"App name: {app_name}")
    
    gp_reviews = gp_scraper.get_reviews(days=config.SCRAPE_DAYS, max_reviews=config.MAX_REVIEWS)
    if not gp_reviews.empty:
        logger.info("Analyzing Google Play reviews...")
        gp_reviews['sentiment_score'] = gp_reviews['review_text'].apply(lambda x: analyzer.analyze_sentiment(x)[1])
        gp_reviews['sentiment'] = gp_reviews['sentiment_score'].apply(
            lambda x: "positive" if x > 0.1 else ("negative" if x < -0.1 else "neutral")
        )
        save_reviews_to_db(gp_reviews, package_name)
        all_reviews.append(gp_reviews)
    else:
        logger.info("No Google Play reviews fetched.")

    # Try to find corresponding Apple App Store app
    apple_id, apple_name = lookup_apple_app(package_name, country)
    
    if not apple_id:
        logger.info("Automatic Apple App Store lookup failed.")
        apple_url = timed_input(
            "Enter Apple App Store URL (5s timeout, press Enter to skip): ",
            timeout=5,
            default=default_apple_url
        )
        
        if not apple_url:
            apple_url = default_apple_url
            logger.info(f"Using default Apple App Store URL: {apple_url}")
        
        apple_url = apple_url.strip()
        if apple_url:
            # Extract ID and country from URL
            # Format: https://apps.apple.com/in/app/zepto-grocery-delivery/id1575323645
            try:
                import re
                id_match = re.search(r'id(\d+)', apple_url)
                country_match = re.search(r'apple\.com/([a-z]{2})/', apple_url)
                
                if id_match:
                    apple_id = id_match.group(1)
                    apple_name = app_name # Use Google Play name as fallback
                    # Update country if found in URL, otherwise keep Google Play country
                    if country_match:
                        country = country_match.group(1)
                    logger.info(f"Extracted Apple App ID: {apple_id}, Country: {country}")
            except Exception as e:
                logger.error(f"Failed to parse Apple URL: {e}")

    if apple_id:
        logger.info(f"Found Apple App Store app: {apple_name} (ID: {apple_id})")
        as_scraper = AppStoreScraper(country=country, app_name=apple_name, app_id=apple_id)
        as_reviews = as_scraper.fetch_reviews(count=config.MAX_REVIEWS, days=config.SCRAPE_DAYS)
        if not as_reviews.empty:
            logger.info("Analyzing Apple App Store reviews...")
            as_reviews['sentiment_score'] = as_reviews['review_text'].apply(lambda x: analyzer.analyze_sentiment(x)[1])
            as_reviews['sentiment'] = as_reviews['sentiment_score'].apply(
                lambda x: "positive" if x > 0.1 else ("negative" if x < -0.1 else "neutral")
            )
            save_reviews_to_db(as_reviews, apple_id)
            all_reviews.append(as_reviews)
            logger.info(f"Added {len(as_reviews)} Apple App Store reviews")
        else:
            logger.info("Apple App Store returned no reviews.")
    else:
        logger.info("Skipping Apple App Store scraping.")

    if all_reviews:
        combined_df = pd.concat(all_reviews, ignore_index=True)
        
        # Cap at 5000 total reviews, keeping the most recent
        if len(combined_df) > 5000:
            combined_df = combined_df.sort_values('review_date', ascending=False).head(5000)
            logger.info(f"Capped total reviews at 5000 (from {len(pd.concat(all_reviews, ignore_index=True))})")
        
        summary = analyzer.generate_summary(combined_df)
        print("\n" + "="*50)
        print("REVIEW SUMMARY REPORT")
        print("="*50)
        print(f"Total Reviews: {summary['total_reviews']}")
        print(f"Average Rating: {summary['average_rating']}")
        print("\nSentiment Distribution:")
        for sentiment, count in summary['sentiment_distribution'].items():
            print(f"  {sentiment}: {count}")
        print("\nTop Keywords:")
        for keyword, count in summary['top_keywords']:
            print(f"  {keyword}: {count}")
        print("\nRecent Critical Reviews:")
        for rev in summary['recent_critical_reviews']:
            print(f"  - [{rev['rating']}*] {rev['review_date']}: {rev['review_text'][:100]}...")
        if config.SMTP_USER and config.SMTP_PASSWORD and config.RECIPIENT_EMAILS:
            logger.info("Sending email report...")
            email_sender = EmailSender(
                smtp_server=config.SMTP_SERVER,
                smtp_port=config.SMTP_PORT,
                username=config.SMTP_USER,
                password=config.SMTP_PASSWORD
            )
            success = email_sender.send_summary_report(
                summary=summary,
                app_name=app_name,
                recipients=[e for e in config.RECIPIENT_EMAILS if e.strip()],
                reviews_df=combined_df,
                days=config.SCRAPE_DAYS
            )
            if success:
                logger.info("Email report sent successfully")
            else:
                logger.error("Failed to send email report")
        else:
            logger.info("Email not configured. Skipping email notification.")
    else:
        logger.info("No reviews fetched from any source.")

if __name__ == "__main__":
    run_scraper()
