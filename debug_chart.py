import logging
import sys
import os
from app_store_review_scraper.notifications.email_sender import EmailSender

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_chart_generation():
    print("Testing chart generation...")
    
    # Initialize EmailSender (dummy creds)
    sender = EmailSender("smtp.gmail.com", 587, "test@example.com", "password")
    
    # Test Data
    scores = [0.5, 0.8, -0.2, 0.1, 0.9, -0.5, 0.3, 0.4, 0.6, 0.7]
    
    # Generate Chart
    print(f"Generating chart with {len(scores)} scores...")
    chart_bytes = sender.create_sentiment_chart(scores)
    
    if chart_bytes:
        print(f"✅ Chart generated successfully! Size: {len(chart_bytes)} bytes")
        
        # Save to file to verify visual
        with open("debug_sentiment_chart.png", "wb") as f:
            f.write(chart_bytes)
        print("✅ Saved to debug_sentiment_chart.png")
    else:
        print("❌ Chart generation returned None")

    # Test with empty data
    print("\nTesting with empty data...")
    chart_bytes_empty = sender.create_sentiment_chart([])
    if chart_bytes_empty is None:
        print("✅ Correctly handled empty data")
    else:
        print("❌ Should return None for empty data")

if __name__ == "__main__":
    try:
        test_chart_generation()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
