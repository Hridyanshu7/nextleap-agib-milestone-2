from google_play_scraper import Sort, reviews, app
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import logging

class GooglePlayScraper:
    """A class to handle scraping of Google Play Store reviews."""

    def __init__(self, app_id: str, lang: str = 'en', country: str = 'us'):
        """Initialize the Google Play Scraper.

        Args:
            app_id (str): The app ID from Google Play Store URL
            lang (str): Language code (default: 'en')
            country (str): Country code (default: 'us')
        """
        self.app_id = app_id
        self.lang = lang
        self.country = country
        self.logger = logging.getLogger(__name__)

    def get_app_name(self) -> Optional[str]:
        """Fetch the app name from Google Play Store.
        
        Returns:
            str: The app name, or None if fetch fails
        """
        try:
            app_details = app(self.app_id, lang=self.lang, country=self.country)
            return app_details.get('title')
        except Exception as e:
            self.logger.error(f"Error fetching app name: {str(e)}")
            return None

    def fetch_reviews(self, days: int = 7, max_reviews: Optional[int] = None) -> List[Dict]:
        """Fetch reviews from Google Play Store.

        Args:
            days (int): Number of days of reviews to fetch (kept for API compatibility but not used)
            max_reviews (int, optional): Maximum number of reviews to fetch
        Returns:
            List[Dict]: List of review dictionaries
        """

        try:
            # Fetch reviews using pagination to reach max_reviews (or 1000)
            fetched = []
            next_token = None
            target_count = max_reviews or 1000
            
            while len(fetched) < target_count:
                # API limit per request is usually around 200, but we can request more and let the library handle it or loop
                # The library 'reviews' function 'count' parameter is for the current batch.
                count = min(200, target_count - len(fetched))
                
                result, next_token = reviews(
                    self.app_id,
                    lang=self.lang,
                    country=self.country,
                    sort=Sort.MOST_RELEVANT,
                    filter_score_with=None,
                    count=count,
                    continuation_token=next_token,
                )
                
                if result:
                    newest_date = result[0]['at']
                    self.logger.info(f"Batch fetched. Newest review in this batch: {newest_date}")

                fetched.extend(result)
                self.logger.info(f"Fetched {len(fetched)} reviews so far...")
                
                if not next_token:
                    break
                    
            self.logger.info(f"Total reviews fetched: {len(fetched)}")
            return fetched
        except Exception as e:
            self.logger.error(f"Error fetching reviews: {str(e)}")
            return []

    def process_reviews(self, reviews: List[Dict]) -> pd.DataFrame:
        """Process raw reviews into a structured DataFrame.

        Args:
            reviews (List[Dict]): List of raw review dictionaries
        Returns:
            pd.DataFrame: Processed reviews in a DataFrame
        """
        if not reviews:
            return pd.DataFrame()
        # Convert to DataFrame
        df = pd.DataFrame(reviews)
        # Standardize column names and add source
        df = df.rename(columns={
            'at': 'review_date',
            'userName': 'user_name',
            'score': 'rating',
            'content': 'review_text',
            'thumbsUpCount': 'thumbs_up',
            'reviewCreatedVersion': 'app_version',
            'replyContent': 'developer_reply',
            'repliedAt': 'reply_date'
        })
        # Add source and processed timestamp
        df['source'] = 'google_play'
        df['processed_at'] = datetime.utcnow()
        # Convert dates to datetime
        date_columns = ['review_date', 'reply_date', 'processed_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        # Extract device information if available
        if 'deviceMetadata' in df.columns:
            df['device'] = df['deviceMetadata'].apply(
                lambda x: x.get('productName', 'unknown') if isinstance(x, dict) else 'unknown'
            )
        else:
            df['device'] = 'unknown'
        return df

    def get_reviews(self, days: int = 7, max_reviews: Optional[int] = None) -> pd.DataFrame:
        """Get reviews and process them into a DataFrame.

        Args:
            days (int): Number of days of reviews to fetch (kept for compatibility)
            max_reviews (int, optional): Maximum number of reviews to fetch
        Returns:
            pd.DataFrame: Processed reviews
        """
        reviews = self.fetch_reviews(days=days, max_reviews=max_reviews)
        return self.process_reviews(reviews)
