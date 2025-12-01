import pandas as pd
from textblob import TextBlob
from typing import Dict, List, Tuple, Optional
from collections import Counter
import re
import logging
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class ReviewAnalyzer:
    """
    A class to analyze app reviews for sentiment and summaries.
    """
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.gemini_model = None
        
        # Initialize Gemini if API key is provided
        if gemini_api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                self.logger.info("Gemini API initialized successfully with gemini-2.5-flash")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Gemini API: {e}. Falling back to basic analysis.")
        elif gemini_api_key and not GEMINI_AVAILABLE:
            self.logger.warning("Gemini API key provided but google-generativeai not installed. Falling back to basic analysis.")
        else:
            self.logger.info("No Gemini API key provided. Using basic analysis.")
        
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
        Group reviews into themes using LLM if available, otherwise use keyword clustering.
        """
        if self.gemini_model:
            return self._extract_themes_llm(df, max_themes)
        else:
            return self._extract_themes_basic(df, max_themes)
    
    def _extract_themes_llm(self, df: pd.DataFrame, max_themes: int = 5) -> List[Tuple[str, int]]:
        """Use Gemini to extract themes from reviews."""
        try:
            # Sample reviews for analysis (max 100 to stay within token limits)
            sample_size = min(100, len(df))
            sample_reviews = df.sample(sample_size)['review_text'].tolist()
            reviews_text = "\n".join([f"- {r[:200]}" for r in sample_reviews if isinstance(r, str)])
            
            prompt = f"""Analyze these app reviews and infer the top {max_themes} broad themes based on the nature of user feedback and sentiment.
Instead of just keywords, identify qualitative themes (e.g., "Unreliable Delivery Service", "App Crashing on Payment", "Excellent Customer Support").

For each theme:
1. Provide a descriptive theme name (3-6 words)
2. Estimate the number of reviews related to this theme

Reviews:
{reviews_text}

Return ONLY a JSON array in this exact format:
[{{"theme": "Descriptive Theme Name", "count": estimated_number}}, ...]

Ensure you return exactly {max_themes} themes. Do not include any other text."""

            response = self.gemini_model.generate_content(prompt)
            result = self._extract_json_from_response(response.text)
            
            # Extrapolate counts to full dataset
            scaling_factor = len(df) / sample_size
            
            themes = []
            for item in result[:max_themes]:
                estimated_count = int(item['count'] * scaling_factor)
                themes.append((item['theme'], estimated_count))
                
            return themes
        except Exception as e:
            self.logger.warning(f"LLM theme extraction failed: {e}. Falling back to basic method.")
            if 'response' in locals():
                self.logger.debug(f"Raw LLM response: {response.text}")
            return self._extract_themes_basic(df, max_themes)
    
    def _extract_json_from_response(self, text: str):
        """Extract JSON from LLM response, handling markdown code blocks and extra text."""
        # Remove markdown code blocks if present
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        # Strip whitespace
        text = text.strip()
        
        # Try to find JSON array or object
        if not text.startswith('[') and not text.startswith('{'):
            # Try to find the first [ or {
            start_bracket = text.find('[')
            start_brace = text.find('{')
            
            if start_bracket != -1 and (start_brace == -1 or start_bracket < start_brace):
                text = text[start_bracket:]
            elif start_brace != -1:
                text = text[start_brace:]
        
        return json.loads(text)
    
    def _extract_themes_basic(self, df: pd.DataFrame, max_themes: int = 5) -> List[Tuple[str, int]]:
        """Basic theme extraction using noun phrase frequency."""
        texts = df['review_text'].tolist()
        all_text = " ".join([self.clean_text(t) for t in texts if isinstance(t, str)])
        blob = TextBlob(all_text)
        noun_phrases = blob.noun_phrases
        
        counts = Counter(noun_phrases)
        filtered_counts = {k: v for k, v in counts.items() if len(k.split()) > 1 or len(k) > 4}
        
        return Counter(filtered_counts).most_common(max_themes)

    def generate_action_ideas(self, df: pd.DataFrame) -> List[str]:
        """
        Generate action ideas based on negative reviews using LLM if available.
        """
        if self.gemini_model:
            return self._generate_action_ideas_llm(df)
        else:
            return self._generate_action_ideas_basic(df)
    
    def _generate_action_ideas_llm(self, df: pd.DataFrame) -> List[str]:
        """Use Gemini to generate actionable insights from negative reviews."""
        try:
            negative_reviews = df[df['sentiment'] == 'negative']
            if negative_reviews.empty:
                return ["Monitor for new feedback", "Engage with positive reviewers", "Maintain current performance"]
            
            # Sample negative reviews
            sample_size = min(50, len(negative_reviews))
            sample_reviews = negative_reviews.sample(sample_size)['review_text'].tolist()
            reviews_text = "\n".join([f"- {r[:200]}" for r in sample_reviews if isinstance(r, str)])
            
            prompt = f"""Based on these negative app reviews, suggest 3 specific, actionable improvements the development team should prioritize.
Make each suggestion concrete and implementable.

Negative Reviews:
{reviews_text}

Return ONLY a JSON array of 3 action items in this exact format:
["Action 1", "Action 2", "Action 3"]

Do not include any other text or explanation."""

            response = self.gemini_model.generate_content(prompt)
            result = self._extract_json_from_response(response.text)
            return result[:3]
        except Exception as e:
            self.logger.warning(f"LLM action ideas generation failed: {e}. Falling back to basic method.")
            return self._generate_action_ideas_basic(df)
    
    def _generate_action_ideas_basic(self, df: pd.DataFrame) -> List[str]:
        """Basic action ideas generation from keywords."""
        negative_reviews = df[df['sentiment'] == 'negative']
        if negative_reviews.empty:
            return ["Monitor for new feedback", "Engage with positive reviewers", "Maintain current performance"]
            
        complaints = self.extract_keywords(negative_reviews['review_text'].tolist(), top_n=3)
        
        actions = []
        for complaint, _ in complaints:
            actions.append(f"Investigate issues related to '{complaint}'")
            
        if not actions:
            actions = ["Review recent negative feedback for specific bugs", "Improve response time to critical reviews", "Check app stability"]
            
        return actions[:3]
    
    def select_representative_quotes(self, df: pd.DataFrame, num_quotes: int = 3) -> List[str]:
        """
        Select representative user quotes using LLM if available.
        """
        if self.gemini_model:
            return self._select_quotes_llm(df, num_quotes)
        else:
            return self._select_quotes_basic(df, num_quotes)
    
    def _select_quotes_llm(self, df: pd.DataFrame, num_quotes: int = 3) -> List[str]:
        """Use Gemini to select the most representative quotes."""
        try:
            # Sample reviews from different sentiment categories
            sample_size = min(50, len(df))
            sample_reviews = df.sample(sample_size)['review_text'].tolist()
            reviews_text = "\n".join([f"- {r[:200]}" for r in sample_reviews if isinstance(r, str)])
            
            prompt = f"""From these app reviews, select {num_quotes} quotes that best represent the overall user experience.
Choose quotes that are:
1. Specific and informative
2. Represent different aspects of the app
3. Are concise and clear

Reviews:
{reviews_text}

Return ONLY a JSON array of {num_quotes} selected quotes in this exact format:
["Quote 1", "Quote 2", "Quote 3"]

Do not include any other text or explanation."""

            response = self.gemini_model.generate_content(prompt)
            result = self._extract_json_from_response(response.text)
            # Scrub PII from selected quotes
            return [self.scrub_pii(quote) for quote in result[:num_quotes]]
        except Exception as e:
            self.logger.warning(f"LLM quote selection failed: {e}. Falling back to basic method.")
            return self._select_quotes_basic(df, num_quotes)
    
    def _select_quotes_basic(self, df: pd.DataFrame, num_quotes: int = 3) -> List[str]:
        """Basic quote selection - random sampling."""
        safe_texts = df['safe_text'] if 'safe_text' in df.columns else df['review_text'].apply(self.scrub_pii)
        return safe_texts.sample(min(num_quotes, len(df))).tolist()

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
            "user_quotes": self.select_representative_quotes(df),
            "action_ideas": self.generate_action_ideas(df)
        }
        
        return summary
