import sys
sys.stdin = open('test_input.txt', 'r')

import logging
logging.basicConfig(level=logging.INFO)

from main import run_scraper
import pandas as pd

# Monkey patch to save the email HTML
from app_store_review_scraper.notifications.email_sender import EmailSender

original_send_email = EmailSender.send_email

def save_html_send_email(self, recipients, subject, html_content, attachment_path=None):
    # Save HTML to file for inspection
    with open('debug_email.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"\n✅ Saved email HTML to debug_email.html (size: {len(html_content)} bytes)")
    
    # Check for Base64 images
    import re
    base64_images = re.findall(r'data:image/png;base64,([A-Za-z0-9+/=]+)', html_content)
    print(f"✅ Found {len(base64_images)} Base64 embedded images")
    for i, img in enumerate(base64_images):
        print(f"   Image {i+1}: {len(img)} characters")
    
    return original_send_email(self, recipients, subject, html_content, attachment_path)

EmailSender.send_email = save_html_send_email

# Monkey patch to intercept the DataFrame
original_concat = pd.concat
def logged_concat(objs, *args, **kwargs):
    result = original_concat(objs, *args, **kwargs)
    print(f"\n=== COMBINED DATAFRAME INFO ===")
    print(f"Total rows: {len(result)}")
    print(f"Date range: {result['review_date'].min()} to {result['review_date'].max()}")
    print(f"\nReviews per source:")
    print(result['source'].value_counts())
    print(f"\nReviews per day (last 10 days):")
    result['date_only'] = pd.to_datetime(result['review_date']).dt.date
    print(result['date_only'].value_counts().sort_index(ascending=False).head(10))
    return result

pd.concat = logged_concat

run_scraper()
