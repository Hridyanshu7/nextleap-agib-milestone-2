import requests
from app_store_scraper import AppStore
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def lookup_apple_app(package_name: str):
    """Check if an app with the given Android package exists on the Apple App Store."""
    try:
        logger.info(f"Looking up {package_name} on iTunes...")
        resp = requests.get('https://itunes.apple.com/lookup', params={'bundleId': package_name}, timeout=10)
        data = resp.json()
        logger.info(f"Lookup response: {data}")
        if data.get('resultCount', 0) > 0:
            result = data['results'][0]
            return str(result.get('trackId')), result.get('trackName')
    except Exception as e:
        logger.error(f"Apple lookup failed: {e}")
    return None, None

def test_apple_scraping(app_name, app_id, country='us'):
    try:
        logger.info(f"Testing scraping for {app_name} (ID: {app_id}, Country: {country})...")
        scraper = AppStore(country=country, app_name=app_name, app_id=app_id)
        reviews = scraper.review(how_many=20)
        logger.info(f"Fetched {len(reviews)} reviews.")
        if reviews:
            logger.info(f"Sample review: {reviews[0]}")
    except Exception as e:
        logger.error(f"Scraping failed: {e}")

if __name__ == "__main__":
    # Test Case 1: Zepto (known package name)
    package_name = "com.zeptoconsumerapp"
    logger.info(f"--- Testing Lookup for {package_name} ---")
    app_id, app_name = lookup_apple_app(package_name)
    
    if app_id:
        logger.info(f"Found: {app_name} (ID: {app_id})")
        # Test scraping with found details
        test_apple_scraping(app_name, app_id)
    else:
        logger.warning("App not found via lookup.")
        
    # Test Case 2: Manual Zepto details (if lookup fails)
    # Zepto iOS ID: 1575323645 (found via web search for verification)
    logger.info("\n--- Testing Manual Scraping for Zepto (IN) ---")
    test_apple_scraping('zepto-10-min-grocery-delivery', '1575323645', country='in')
