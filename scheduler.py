import schedule
import time
import logging
from datetime import datetime
from main import run_scraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def job():
    """
    Job to run the scraper.
    """
    logger.info("Starting scheduled scraper job...")
    try:
        run_scraper()
        logger.info("Scheduled scraper job completed successfully")
    except Exception as e:
        logger.error(f"Error in scheduled job: {str(e)}")

def run_scheduler():
    """
    Run the scheduler for weekly reports.
    """
    # Schedule the job to run every Monday at 9:00 AM
    schedule.every().monday.at("09:00").do(job)
    
    # For testing, you can also schedule it to run every N minutes
    # schedule.every(5).minutes.do(job)
    
    logger.info("Scheduler started. Waiting for scheduled tasks...")
    logger.info("Next run: " + str(schedule.next_run()))
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Run once immediately on startup
    logger.info("Running initial scraper job...")
    job()
    
    # Then start the scheduler
    run_scheduler()
