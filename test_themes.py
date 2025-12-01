import pandas as pd
import logging
import config
from app_store_review_scraper.analysis.summarizer import ReviewAnalyzer

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Sample reviews (simulating real data)
reviews_data = [
    "The app keeps crashing when I try to pay. It's so frustrating!",
    "Delivery was super fast, got my groceries in 10 mins.",
    "Customer support is terrible, they never reply.",
    "Payment failed multiple times but money was deducted.",
    "Love the quick delivery service!",
    "App is very slow and laggy on my phone.",
    "Refund process is a nightmare.",
    "Best grocery app ever, very convenient.",
    "Rude delivery partner, threw my package.",
    "Cannot add items to cart, button not working."
] * 5  # Duplicate to have enough data

df = pd.DataFrame({'review_text': reviews_data})

print("Initializing ReviewAnalyzer...")
analyzer = ReviewAnalyzer(gemini_api_key=config.GEMINI_API_KEY)

print("\nTesting Theme Extraction...")
themes = analyzer.extract_themes(df, max_themes=5)

print("\nExtracted Themes:")
for theme, count in themes:
    print(f"- {theme}: {count}")
