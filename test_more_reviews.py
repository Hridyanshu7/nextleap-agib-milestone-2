from google_play_scraper import Sort, reviews
from datetime import datetime
import pandas as pd

package_name = "com.zeptoconsumerapp"

print("=== Testing with increased count ===\n")

# Try fetching MORE 1-star reviews
all_reviews = []
continuation_token = None

for batch in range(1, 6):  # Try 5 batches
    result, continuation_token = reviews(
        package_name,
        lang='en',
        country='in',
        sort=Sort.NEWEST,
        filter_score_with=1,
        count=200,
        continuation_token=continuation_token
    )
    
    print(f"Batch {batch}: Fetched {len(result)} reviews")
    all_reviews.extend(result)
    
    if not continuation_token:
        print("No more reviews available")
        break

print(f"\nTotal 1-star reviews fetched: {len(all_reviews)}")

df = pd.DataFrame(all_reviews)
df['date'] = pd.to_datetime(df['at'])
df['date_only'] = df['date'].dt.date

nov_30 = df[df['date_only'] == pd.to_datetime('2025-11-30').date()]
print(f"1-star reviews from Nov 30: {len(nov_30)}")

print(f"\nNewest: {df.iloc[0]['date']}")
print(f"Oldest: {df.iloc[-1]['date']}")

# Check for RAVI
ravi = df[df['userName'].str.contains('RAVI', case=False, na=False)]
print(f"\nRAVI reviews found: {len(ravi)}")
