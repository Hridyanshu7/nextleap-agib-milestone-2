from google_play_scraper import Sort, reviews
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_play_scraping(package_name, lang='en', country='in', sort_order=Sort.NEWEST):
    logger.info(f"Testing Google Play scraping for {package_name} (Sort: {sort_order})...")
    
    try:
        result, _ = reviews(
            package_name,
            lang=lang,
            country=country,
            sort=sort_order,
            count=100  # Fetch 100 to check recency
        )
        
        logger.info(f"Fetched {len(result)} reviews.")
        
        if result:
            dates = [r['at'] for r in result]
            newest = max(dates)
            oldest = min(dates)
            logger.info(f"Newest review: {newest}")
            logger.info(f"Oldest review: {oldest}")
            
            # Check for reviews in last 5 days
            now = datetime.now()
            recent_count = sum(1 for d in dates if (now - d).days <= 5)
            logger.info(f"Reviews in last 5 days: {recent_count}")
            
            # Print first few dates to check order
            logger.info("First 5 review dates:")
            for r in result[:5]:
                logger.info(f"- {r['at']}")
                
    except Exception as e:
        logger.error(f"Scraping failed: {e}")

if __name__ == "__main__":
    package_name = "com.zeptoconsumerapp"
    
    logger.info("--- Testing Sort.NEWEST ---")
    test_play_scraping(package_name, sort_order=Sort.NEWEST)
    
    logger.info("\n--- Testing Sort.MOST_RELEVANT ---")
    test_play_scraping(package_name, sort_order=Sort.MOST_RELEVANT)
