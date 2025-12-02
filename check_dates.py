from google_play_scraper import Sort, reviews
from datetime import datetime
import pandas as pd

# Fetch reviews and check dates
package_name = "com.zeptoconsumerapp"
result, _ = reviews(
    package_name,
    lang='en',
    country='in',
    sort=Sort.NEWEST,
    count=200  # Fetch more to see the pattern
)

# Sort by date
result.sort(key=lambda x: x['at'], reverse=True)

# Create DataFrame
df = pd.DataFrame(result)
df['date'] = pd.to_datetime(df['at'])

# Check date distribution
print("Date distribution of first 50 reviews:")
print(df.head(50)['date'].dt.date.value_counts().sort_index(ascending=False))

print("\nFirst 10 review dates:")
for i, row in df.head(10).iterrows():
    print(f"{i+1}. {row['date']} - {row['content'][:50]}")

print(f"\nNewest review: {df.iloc[0]['date']}")
print(f"Oldest review in batch: {df.iloc[-1]['date']}")
