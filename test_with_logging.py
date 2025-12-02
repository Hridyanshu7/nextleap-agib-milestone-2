import sys
sys.stdin = open('test_input.txt', 'r')

import logging
logging.basicConfig(level=logging.INFO)

from main import run_scraper
import pandas as pd

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
