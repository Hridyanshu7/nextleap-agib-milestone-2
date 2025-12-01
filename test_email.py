"""
Test script for email functionality.
This will send a test email with sample review data.
"""

import logging
from datetime import datetime, timedelta
from app_store_review_scraper.notifications.email_sender import EmailSender
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_sample_summary():
    """Create sample summary data for testing"""
    return {
        'total_reviews': 10,  # Matches the 10 reviews in Excel
        'average_rating': 3.0,  # Average of [5,4,3,2,1,5,4,3,2,1]
        'sentiment_distribution': {
            'positive': 4,
            'neutral': 2,
            'negative': 4
        },
        'top_keywords': [
            ('app crashes', 2),
            ('great features', 2),
            ('customer support', 1),
            ('latest update', 1),
            ('highly recommend', 1),
            ('easy to use', 1),
            ('user interface', 1),
            ('experience', 2)
        ],
        'recent_critical_reviews': [
            {
                'rating': 1,
                'review_date': datetime.now() - timedelta(days=4),
                'review_text': 'App keeps crashing. Very frustrating.'
            },
            {
                'rating': 2,
                'review_date': datetime.now() - timedelta(days=3),
                'review_text': 'Not satisfied with the latest update.'
            },
            {
                'rating': 1,
                'review_date': datetime.now(),
                'review_text': 'Terrible experience. Uninstalling.'
            }
        ]
    }

def create_sample_reviews_df():
    """Create sample reviews DataFrame for Excel attachment"""
    import pandas as pd
    
    data = {
        'review_date': [
            datetime.now() - timedelta(days=i) for i in range(10)
        ],
        'source': ['google_play'] * 5 + ['app_store'] * 5,
        'user_name': [f'User{i}' for i in range(10)],
        'rating': [5, 4, 3, 2, 1, 5, 4, 3, 2, 1],
        'review_text': [
            'Great app! Love all the features.',
            'Good app but needs some improvements.',
            'Average experience. Could be better.',
            'Not satisfied with the latest update.',
            'App keeps crashing. Very frustrating.',
            'Excellent! Highly recommend.',
            'Pretty good overall.',
            'Okay, nothing special.',
            'Disappointed with customer support.',
            'Terrible experience. Uninstalling.'
        ],
        'sentiment': ['positive', 'positive', 'neutral', 'negative', 'negative',
                     'positive', 'positive', 'neutral', 'negative', 'negative'],
        'sentiment_score': [0.8, 0.6, 0.1, -0.4, -0.8, 0.9, 0.5, 0.0, -0.5, -0.9],
        'app_version': ['2.1.0'] * 10,
        'developer_reply': [None] * 8 + ['Thank you for your feedback.', 'We apologize for the inconvenience.'],
        'reply_date': [None] * 8 + [datetime.now() - timedelta(days=1), datetime.now() - timedelta(days=2)],
        'device': ['Pixel 6', 'Samsung S21', 'OnePlus 9', 'iPhone 13', 'iPhone 12',
                  'iPhone 14', 'Pixel 7', 'Samsung S22', 'OnePlus 10', 'iPhone 11']
    }
    
    return pd.DataFrame(data)

def test_email():
    """Test email sending functionality"""
    
    # Get email configuration from environment
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    recipients = os.getenv('RECIPIENT_EMAILS', '').split(',')
    
    # Validate configuration
    if not smtp_user or not smtp_password:
        logger.error("❌ Email credentials not configured!")
        logger.info("Please set SMTP_USER and SMTP_PASSWORD in your .env file")
        logger.info("\nFor Gmail:")
        logger.info("1. Go to https://myaccount.google.com/security")
        logger.info("2. Enable 2-Step Verification")
        logger.info("3. Generate App Password at https://myaccount.google.com/apppasswords")
        logger.info("4. Add to .env file:")
        logger.info("   SMTP_USER=your-email@gmail.com")
        logger.info("   SMTP_PASSWORD=your-16-char-app-password")
        logger.info("   RECIPIENT_EMAILS=recipient@example.com")
        return False
    
    if not recipients or recipients == ['']:
        logger.error("❌ No recipient emails configured!")
        logger.info("Please set RECIPIENT_EMAILS in your .env file")
        return False
    
    # Clean up recipient list
    recipients = [email.strip() for email in recipients if email.strip()]
    
    logger.info("📧 Email Configuration:")
    logger.info(f"   SMTP Server: {smtp_server}:{smtp_port}")
    logger.info(f"   From: {smtp_user}")
    logger.info(f"   To: {', '.join(recipients)}")
    
    # Create email sender
    email_sender = EmailSender(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        username=smtp_user,
        password=smtp_password
    )
    
    # Create sample summary
    logger.info("\n📊 Creating sample review summary...")
    summary = create_sample_summary()
    
    # Create sample reviews DataFrame
    logger.info("📄 Creating sample reviews data for Excel...")
    reviews_df = create_sample_reviews_df()
    
    # Send test email
    logger.info("\n📤 Sending test email with Excel attachment...")
    success = email_sender.send_summary_report(
        summary=summary,
        app_name="Test App (Sample Data)",
        recipients=recipients,
        reviews_df=reviews_df,
        days=7
    )
    
    if success:
        logger.info("\n✅ Test email sent successfully!")
        logger.info(f"Check your inbox at: {', '.join(recipients)}")
        return True
    else:
        logger.error("\n❌ Failed to send test email")
        logger.info("Common issues:")
        logger.info("1. Incorrect email/password")
        logger.info("2. Need to use App Password for Gmail (not regular password)")
        logger.info("3. 2-Step Verification not enabled")
        logger.info("4. SMTP server/port incorrect")
        return False

if __name__ == "__main__":
    print("="*60)
    print("EMAIL FUNCTIONALITY TEST")
    print("="*60)
    print()
    
    test_email()
