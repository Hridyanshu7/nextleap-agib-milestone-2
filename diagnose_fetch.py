from google_play_scraper import Sort, reviews
from datetime import datetime, timedelta
import pandas as pd

package_name = "com.zeptoconsumerapp"

print("Testing different fetch strategies...\n")

# Strategy 1: Single large fetch
print("=== Strategy 1: Single fetch of 1000 ===")
result1, token1 = reviews(
    package_name,
    lang='en',
    country='in',
    sort=Sort.NEWEST,
    count=1000
)
print(f"Fetched: {len(result1)} reviews")
df1 = pd.DataFrame(result1)
df1['date'] = pd.to_datetime(df1['at'])

# Count reviews per day for last 7 days
cutoff = datetime.now() - timedelta(days=7)
recent = df1[df1['date'] >= cutoff]
print(f"Reviews in last 7 days: {len(recent)}")
print("\nDate distribution (last 7 days):")
print(recent['date'].dt.date.value_counts().sort_index(ascending=False))

# Strategy 2: Multiple batches with continuation token
print("\n=== Strategy 2: Pagination with continuation token ===")
all_reviews = []
continuation_token = None
batch_num = 0

while len(all_reviews) < 1000:
    batch_num += 1
    result, continuation_token = reviews(
        package_name,
        lang='en',
        country='in',
        sort=Sort.NEWEST,
        count=200,
        continuation_token=continuation_token
    )
    
    if not result:
        print(f"No more reviews after batch {batch_num}")
        break
        
    all_reviews.extend(result)
    print(f"Batch {batch_num}: Fetched {len(result)} reviews (Total: {len(all_reviews)})")
    
    if not continuation_token:
        print("No continuation token - reached end")
        break

df2 = pd.DataFrame(all_reviews)
df2['date'] = pd.to_datetime(df2['at'])
recent2 = df2[df2['date'] >= cutoff]
print(f"\nTotal reviews fetched: {len(all_reviews)}")
print(f"Reviews in last 7 days: {len(recent2)}")
print("\nDate distribution (last 7 days):")
print(recent2['date'].dt.date.value_counts().sort_index(ascending=False))
