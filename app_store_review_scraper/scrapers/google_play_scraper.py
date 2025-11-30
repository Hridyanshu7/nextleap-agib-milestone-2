from google_play_scraper import Sort, reviews_all
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import logging

class GooglePlayScraper:
    """
    A class to handle scraping of Google Play Store reviews.
    """
    
    def __init__(self, app_id: str, lang: str = 'en', country: str = 'us'):
        """
        Initialize the Google Play Scraper.
        
        Args:
            app_id (str): The app ID from Google Play Store URL
            lang (str): Language code (default: 'en')
            country (str): Country code (default: 'us')
        """
        self.app_id = app_id
        self.lang = lang
        self.country = country
        self.logger = logging.getLogger(__name__)
    
    def fetch_reviews(self, 
                     days: int = 7, 
                     max_reviews: Optional[int] = None) -> List[Dict]:
        """
        Fetch reviews from Google Play Store.
        
        Args:
            days (int): Number of days of reviews to fetch
            max_reviews (int, optional): Maximum number of reviews to fetch
            
        Returns:
            List[Dict]: List of review dictionaries
        """
        try:
            # Calculate the date from which to fetch reviews
            after = datetime.now() - timedelta(days=days)
            
            # Fetch reviews
            result = reviews_all(
                self.app_id,
                lang=self.lang,
                country=self.country,
                sort=Sort.NEWEST,
                filter_score_with=None,  # Get all scores
                count=max_reviews or 200,  # Default to 200 if max_reviews not specified
            )
            
            # Filter reviews by date
            filtered_reviews = [
                review for review in result 
                if datetime.fromtimestamp(review['at'].timestamp()) >= after
            ]
            
            self.logger.info(f"Fetched {len(filtered_reviews)} reviews from Google Play Store")
            return filtered_reviews
            
        except Exception as e:
            self.logger.error(f"Error fetching reviews: {str(e)}")
            return []
    
    def process_reviews(self, reviews: List[Dict]) -> pd.DataFrame:
        """
        Process raw reviews into a structured DataFrame.
        
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
        df['device'] = df.get('deviceMetadata', {}).apply(
            lambda x: x.get('productName', 'unknown') if isinstance(x, dict) else 'unknown'
        )
        
        return df
    
    def get_reviews(self, days: int = 7, max_reviews: Optional[int] = None) -> pd.DataFrame:
        """
        Get reviews and process them into a DataFrame.
        
        Args:
            days (int): Number of days of reviews to fetch
            max_reviews (int, optional): Maximum number of reviews to fetch
            
        Returns:
            pd.DataFrame: Processed reviews
        """
        reviews = self.fetch_reviews(days=days, max_reviews=max_reviews)
        return self.process_reviews(reviews)
