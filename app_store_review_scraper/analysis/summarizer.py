import pandas as pd
from textblob import TextBlob
from typing import Dict, List, Tuple
from collections import Counter
import re
import logging

class ReviewAnalyzer:
    """
    A class to analyze app reviews for sentiment and summaries.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def clean_text(self, text: str) -> str:
        """
        Clean review text by removing special characters and extra whitespace.
        """
        if not isinstance(text, str):
            return ""
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?]', '', text)
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """
        Analyze sentiment of a text.
        Returns (sentiment_category, polarity_score)
        """
        if not text:
            return "neutral", 0.0
            
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return "positive", polarity
        elif polarity < -0.1:
            return "negative", polarity
        else:
            return "neutral", polarity
            
    def extract_keywords(self, texts: List[str], top_n: int = 10) -> List[Tuple[str, int]]:
        """
        Extract most common keywords/noun phrases from a list of texts.
        """
        all_text = " ".join([self.clean_text(t) for t in texts if isinstance(t, str)])
        blob = TextBlob(all_text)
        
        # Get noun phrases
        noun_phrases = blob.noun_phrases
        
        # Count frequencies
        counts = Counter(noun_phrases)
        return counts.most_common(top_n)
    
    def scrub_pii(self, text: str) -> str:
        """
        Remove potential PII (emails, phone numbers) from text.
        """
        if not isinstance(text, str):
            return ""
        # Email regex
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
        # Phone regex (simple)
        text = re.sub(r'\b\d{10}\b|\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
        return text

    def extract_themes(self, df: pd.DataFrame, max_themes: int = 5) -> List[Tuple[str, int]]:
        """
        Group reviews into themes using keyword clustering or simple frequency.
        For simplicity and robustness without heavy ML dependencies, we'll use 
        noun phrase frequency mapping to broader categories if possible, 
        or just return the top distinct noun phrases as themes.
        """
        # Get all noun phrases
        texts = df['review_text'].tolist()
        all_text = " ".join([self.clean_text(t) for t in texts if isinstance(t, str)])
        blob = TextBlob(all_text)
        noun_phrases = blob.noun_phrases
        
        # Count frequencies
        counts = Counter(noun_phrases)
        
        # Filter out very short or generic phrases
        filtered_counts = {k: v for k, v in counts.items() if len(k.split()) > 1 or len(k) > 4}
        
        # Return top N themes
        return Counter(filtered_counts).most_common(max_themes)

    def generate_action_ideas(self, df: pd.DataFrame) -> List[str]:
        """
        Generate action ideas based on negative reviews.
        """
        negative_reviews = df[df['sentiment'] == 'negative']
        if negative_reviews.empty:
            return ["Monitor for new feedback", "Engage with positive reviewers", "Maintain current performance"]
            
        # Extract common complaints (keywords in negative reviews)
        complaints = self.extract_keywords(negative_reviews['review_text'].tolist(), top_n=3)
        
        actions = []
        for complaint, _ in complaints:
            actions.append(f"Investigate issues related to '{complaint}'")
            
        if not actions:
            actions = ["Review recent negative feedback for specific bugs", "Improve response time to critical reviews", "Check app stability"]
            
        return actions[:3]

    def generate_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate a summary report from a DataFrame of reviews.
        """
        if df.empty:
            return {
                "total_reviews": 0,
                "average_rating": 0,
                "sentiment_distribution": {},
                "top_keywords": [],
                "recent_critical_reviews": [],
                "top_themes": [],
                "user_quotes": [],
                "action_ideas": []
            }
            
        # Ensure we have sentiment
        if 'sentiment_score' not in df.columns:
            df['sentiment_score'] = df['review_text'].apply(
                lambda x: self.analyze_sentiment(x)[1]
            )
            df['sentiment'] = df['sentiment_score'].apply(
                lambda x: "positive" if x > 0.1 else ("negative" if x < -0.1 else "neutral")
            )
            
        # Scrub PII for reporting
        df['safe_text'] = df['review_text'].apply(self.scrub_pii)
            
        summary = {
            "total_reviews": len(df),
            "average_rating": round(df['rating'].mean(), 2),
            "sentiment_distribution": df['sentiment'].value_counts().to_dict(),
            "top_keywords": self.extract_keywords(df['review_text'].tolist()),
            "recent_critical_reviews": df[
                (df['rating'] <= 2) | (df['sentiment'] == 'negative')
            ].sort_values('review_date', ascending=False).head(5)[['review_date', 'rating', 'safe_text']].rename(columns={'safe_text': 'review_text'}).to_dict('records'),
            "top_themes": self.extract_themes(df),
            "user_quotes": df.sample(min(3, len(df)))['safe_text'].tolist(),
            "action_ideas": self.generate_action_ideas(df)
        }
        
        return summary
