import requests
from app_store_review_scraper.scrapers.app_store_scraper import AppStoreScraper
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_apple_rss_scraping(app_id, country='in'):
    logger.info(f"Testing Apple RSS scraping for ID: {app_id} (Country: {country})...")
    
    scraper = AppStoreScraper(country=country, app_name="Test App", app_id=app_id)
    reviews = scraper.fetch_reviews(count=100)
    
    logger.info(f"Fetched {len(reviews)} reviews.")
    
    if not reviews.empty:
        logger.info(f"Columns: {reviews.columns.tolist()}")
        logger.info(f"First review date: {reviews.iloc[0]['review_date']}")
        logger.info(f"Last review date: {reviews.iloc[-1]['review_date']}")
        logger.info(f"Sample review text: {reviews.iloc[0]['review_text'][:50]}...")
    else:
        logger.warning("No reviews fetched.")

if __name__ == "__main__":
    # Zepto iOS ID: 1575323645
    test_apple_rss_scraping('1575323645', country='in')
