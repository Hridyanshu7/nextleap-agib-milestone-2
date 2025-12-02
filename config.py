import os
from dotenv import load_dotenv

load_dotenv()

# App Configuration
# Format: {'app_name': {'google_play': 'package_name', 'app_store': 'app_id'}}
APPS = {
    'example_app': {
        'google_play': 'com.whatsapp',  # Example: WhatsApp
        'app_store': {
            'name': 'whatsapp-messenger',
            'id': '310633997'
        }
    }
}

# Scraper Settings
SCRAPE_DAYS = int(os.getenv('SCRAPE_DAYS', 7))
MAX_REVIEWS = int(os.getenv('MAX_REVIEWS', 5000))

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///reviews.db')

# Email Settings (for later)
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
RECIPIENT_EMAILS = os.getenv('RECIPIENT_EMAILS', '').split(',')

# LLM Settings (Optional - for enhanced analysis)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
