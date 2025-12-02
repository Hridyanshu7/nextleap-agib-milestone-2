import pandas as pd
import matplotlib.pyplot as plt
from app_store_review_scraper.notifications.email_sender import EmailSender
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_rating_chart():
    sender = EmailSender("smtp.gmail.com", 587, "test@example.com", "password")
    
    # Test case 1: Normal data
    ratings = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]
    print(f"Testing with ratings: {ratings}")
    
    chart_bytes = sender.create_rating_distribution_chart(ratings)
    
    if chart_bytes:
        print(f"✅ Chart generated successfully! Size: {len(chart_bytes)} bytes")
        with open("debug_rating_chart.png", "wb") as f:
            f.write(chart_bytes)
        print("✅ Saved to debug_rating_chart.png")
    else:
        print("❌ Chart generation returned None")

    # Test case 2: Missing some ratings
    ratings_missing = [1, 1, 5, 5]
    print(f"\nTesting with missing ratings: {ratings_missing}")
    chart_bytes_missing = sender.create_rating_distribution_chart(ratings_missing)
    
    if chart_bytes_missing:
        print(f"✅ Chart generated successfully! Size: {len(chart_bytes_missing)} bytes")
        with open("debug_rating_chart_missing.png", "wb") as f:
            f.write(chart_bytes_missing)
        print("✅ Saved to debug_rating_chart_missing.png")
    else:
        print("❌ Chart generation returned None")

if __name__ == "__main__":
    test_rating_chart()
