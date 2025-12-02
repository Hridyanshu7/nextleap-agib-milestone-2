from google_play_scraper import Sort, reviews
from datetime import datetime, timedelta
import pandas as pd

package_name = "com.zeptoconsumerapp"

print("=== Diagnosing 1-star review fetching ===\n")

# Fetch 1-star reviews
result, _ = reviews(
    package_name,
    lang='en',
    country='in',
    sort=Sort.NEWEST,
    filter_score_with=1,
    count=500  # Fetch more to see what we get
)

print(f"Total 1-star reviews fetched: {len(result)}\n")

# Convert to DataFrame
df = pd.DataFrame(result)
df['date'] = pd.to_datetime(df['at'])
df['date_only'] = df['date'].dt.date

# Filter for Nov 30
nov_30 = df[df['date_only'] == pd.to_datetime('2025-11-30').date()]
print(f"1-star reviews from Nov 30: {len(nov_30)}")

# Check for RAVI JOUNKANI
ravi_reviews = df[df['userName'].str.contains('RAVI', case=False, na=False)]
print(f"\nReviews from users with 'RAVI' in name: {len(ravi_reviews)}")
if not ravi_reviews.empty:
    print("RAVI review details:")
    for idx, row in ravi_reviews.iterrows():
        print(f"  - {row['userName']}: {row['date']} - {row['content'][:50]}")
else:
    print("  RAVI JOUNKANI not found in fetched reviews!")

print("\nFirst 10 review dates:")
for i, row in df.head(10).iterrows():
    print(f"{i+1}. {row['date']} - {row['userName']} - {row['content'][:50]}")

print(f"\nDate distribution:")
print(df['date_only'].value_counts().sort_index(ascending=False).head(10))

# Check if we're hitting the API limit
print(f"\nNewest review: {df.iloc[0]['date']}")
print(f"Oldest review: {df.iloc[-1]['date']}")
