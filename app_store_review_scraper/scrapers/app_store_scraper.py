import requests
import pandas as pd
from datetime import datetime
import logging
from typing import List, Dict, Optional
import time

class AppStoreScraper:
    def __init__(self, country: str = 'us', app_name: str = None, app_id: str = None):
        self.country = country
        self.app_name = app_name
        self.app_id = app_id
        self.logger = logging.getLogger(__name__)

    def fetch_reviews(self, count: int = 100, days: int = 7) -> pd.DataFrame:
        """
        Fetch reviews from Apple App Store using RSS feed.
        
        Args:
            count (int): Number of reviews to fetch (max effective ~5000)
            days (int): Number of days to look back
            
        Returns:
            pd.DataFrame: DataFrame containing reviews
        """
        from datetime import datetime, timedelta
        
        try:
            if not self.app_id:
                self.logger.error("App ID is required for Apple App Store scraping")
                return pd.DataFrame()

            cutoff_date = datetime.now() - timedelta(days=days)
            all_reviews = []
            pages_to_fetch = min((count // 50) + 1, 100)  # Max 100 pages
            
            for page in range(1, pages_to_fetch + 1):
                url = f"https://itunes.apple.com/{self.country}/rss/customerreviews/page={page}/id={self.app_id}/sortby=mostrecent/json"
                self.logger.info(f"Fetching Apple reviews page {page}...")
                
                response = requests.get(url, timeout=15)
                
                if response.status_code != 200:
                    self.logger.warning(f"Failed to fetch page {page}: Status {response.status_code}")
                    break
                    
                data = response.json()
                feed = data.get('feed', {})
                entries = feed.get('entry', [])
                
                if not entries:
                    break
                
                page_has_recent = False
                    
                for entry in entries:
                    if 'im:name' in entry: 
                        continue
                        
                    try:
                        review_date_raw = datetime.fromisoformat(entry.get('updated', {}).get('label').replace('Z', '+00:00'))
                        # Convert to naive datetime for comparison
                        review_date_naive = review_date_raw.replace(tzinfo=None)
                        
                        # Stop if we've gone past the cutoff date
                        if review_date_naive < cutoff_date:
                            continue
                        
                        page_has_recent = True
                        review = {
                            'review_id': entry.get('id', {}).get('label'),
                            'user_name': entry.get('author', {}).get('name', {}).get('label'),
                            'review_date': review_date_raw,
                            'rating': int(entry.get('im:rating', {}).get('label', 0)),
                            'review_title': entry.get('title', {}).get('label'),
                            'review_text': entry.get('content', {}).get('label'),
                            'thumbs_up': int(entry.get('im:voteCount', {}).get('label', 0)),
                            'version': entry.get('im:version', {}).get('label'),
                            'source': 'app_store',
                            'app_name': self.app_name,
                            'sentiment_score': 0.0,
                            'sentiment': 'neutral'
                        }
                        all_reviews.append(review)
                    except Exception as e:
                        self.logger.warning(f"Error parsing review entry: {e}")
                        continue
                
                # Stop if this page had no recent reviews
                if not page_has_recent:
                    self.logger.info(f"No more reviews from last {days} days, stopping at page {page}")
                    break
                
                if len(all_reviews) >= count:
                    break
                    
                time.sleep(1)

            df = pd.DataFrame(all_reviews)
            
            if not df.empty:
                # Convert to UTC and remove timezone info
                df['review_date'] = pd.to_datetime(df['review_date']).dt.tz_convert('UTC').dt.tz_localize(None)
                self.logger.info(f"Successfully fetched {len(df)} reviews from Apple App Store (last {days} days)")
            
            return df

        except Exception as e:
            self.logger.error(f"Error fetching Apple reviews: {str(e)}")
            return pd.DataFrame()
