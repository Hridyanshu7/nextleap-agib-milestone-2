from app_store_scraper import AppStore
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import logging
import time

class AppStoreScraper:
    """
    A class to handle scraping of Apple App Store reviews.
    """
    
    def __init__(self, app_name: str, app_id: str, country: str = 'us'):
        """
        Initialize the App Store Scraper.
        
        Args:
            app_name (str): The app name (slug) used in App Store URL
            app_id (str): The app ID (numbers only)
            country (str): Country code (default: 'us')
        """
        self.app_name = app_name
        self.app_id = app_id
        self.country = country
        self.logger = logging.getLogger(__name__)
        self.app = AppStore(country=self.country, app_name=self.app_name, app_id=self.app_id)
    
    def fetch_reviews(self, 
                     days: int = 7, 
                     max_reviews: Optional[int] = None) -> List[Dict]:
        """
        Fetch reviews from Apple App Store.
        
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
            # Note: app_store_scraper doesn't support date filtering in the API call directly,
            # so we might need to fetch more and filter locally.
            # However, it fetches newest first.
            
            count = max_reviews or 200
            self.app.review(how_many=count)
            
            result = self.app.reviews
            
            # Filter reviews by date
            filtered_reviews = [
                review for review in result 
                if review['date'] >= after
            ]
            
            self.logger.info(f"Fetched {len(filtered_reviews)} reviews from App Store")
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
        
        # Standardize column names
        # App Store fields: date, review, rating, isEdited, userName, title, developerResponse
        df = df.rename(columns={
            'date': 'review_date',
            'userName': 'user_name',
            'review': 'review_text',
            'isEdited': 'is_edited'
        })
        
        # Handle developer response if present
        if 'developerResponse' in df.columns:
            df['developer_reply'] = df['developerResponse'].apply(
                lambda x: x.get('body') if isinstance(x, dict) else None
            )
            df['reply_date'] = df['developerResponse'].apply(
                lambda x: x.get('modified') if isinstance(x, dict) else None
            )
        else:
            df['developer_reply'] = None
            df['reply_date'] = None
            
        # Add source and processed timestamp
        df['source'] = 'app_store'
        df['processed_at'] = datetime.utcnow()
        
        # Ensure other standard columns exist (fill with None/defaults)
        if 'thumbs_up' not in df.columns:
            df['thumbs_up'] = 0
        if 'app_version' not in df.columns:
            df['app_version'] = None
        if 'device' not in df.columns:
            df['device'] = None
            
        # Convert dates to datetime
        date_columns = ['review_date', 'reply_date', 'processed_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
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
