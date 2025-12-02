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

    def fetch_reviews(self, days: int = 7, max_reviews: Optional[int] = None) -> pd.DataFrame:
        """Fetch reviews from Google Play Store by rating to maximize coverage.
        
        Args:
            days (int): Number of days of reviews to fetch
            max_reviews (int, optional): Maximum total reviews to fetch (default: 5000)
            
        Returns:
            pd.DataFrame: DataFrame containing reviews
        """
        from datetime import datetime, timedelta
        
        max_reviews = max_reviews or 5000
        cutoff_date = datetime.now() - timedelta(days=days)
        
        all_reviews = []
        seen_ids = set()
        
        try:
            # Fetch reviews for each rating (1-5 stars)
            for rating in [1, 2, 3, 4, 5]:
                if len(all_reviews) >= max_reviews:
                    self.logger.info(f"Reached max_reviews limit ({max_reviews}), stopping")
                    break
                    
                self.logger.info(f"Fetching {rating}-star reviews...")
                rating_reviews = []
                continuation_token = None
                
                # Fetch up to 1000 reviews per rating
                while len(rating_reviews) < 1000:
                    try:
                        result, continuation_token = reviews(
                            self.app_id,
                            lang=self.lang,
                            country=self.country,
                            sort=Sort.NEWEST,
                            filter_score_with=rating,
                            count=200,
                            continuation_token=continuation_token
                        )
                        
                        if not result:
                            break
                        
                        rating_reviews.extend(result)
                        
                        if not continuation_token:
                            break
                            
                    except Exception as e:
                        self.logger.warning(f"Error fetching {rating}-star reviews: {e}")
                        break
                
                # Filter for last N days and deduplicate
                for review in rating_reviews:
                    review_id = review.get('reviewId')
                    review_date = review.get('at')
                    
                    if review_id and review_id not in seen_ids and review_date >= cutoff_date:
                        all_reviews.append(review)
                        seen_ids.add(review_id)
                        
                        if len(all_reviews) >= max_reviews:
                            break
                
                self.logger.info(f"Added {len([r for r in rating_reviews if r.get('at') >= cutoff_date])} {rating}-star reviews from last {days} days")
            
            # Client-side sort to ensure strict date ordering
            all_reviews.sort(key=lambda x: x['at'], reverse=True)
            self.logger.info(f"Total reviews fetched: {len(all_reviews)} (from last {days} days)")
            
            # Process reviews to DataFrame
            return self.process_reviews(all_reviews)
            
        except Exception as e:
            self.logger.error(f"Error fetching reviews: {str(e)}")
            return pd.DataFrame()

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
        return self.fetch_reviews(days=days, max_reviews=max_reviews)
