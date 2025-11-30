from sqlalchemy import Column, String, Integer, DateTime, Text, Float, Boolean, ForeignKey, Enum
from datetime import datetime
from .base import Base, BaseModel
import enum

class ReviewSource(enum.Enum):
    GOOGLE_PLAY = "google_play"
    APP_STORE = "app_store"

class ReviewSentiment(enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class Review(Base, BaseModel):
    """Model to store app reviews"""
    __tablename__ = "reviews"
    
    # Core review data
    review_id = Column(String(255), unique=True, index=True, nullable=False)
    source = Column(Enum(ReviewSource), nullable=False)
    app_id = Column(String(255), index=True, nullable=False)
    app_version = Column(String(100))
    
    # User information
    user_name = Column(String(255))
    user_image = Column(String(500))
    
    # Review content
    rating = Column(Integer, nullable=False)  # 1-5 stars
    title = Column(String(500))
    content = Column(Text)
    
    # Sentiment analysis
    sentiment = Column(Enum(ReviewSentiment))
    sentiment_score = Column(Float)  # -1.0 to 1.0
    
    # Metadata
    review_date = Column(DateTime, nullable=False)
    country = Column(String(50))
    language = Column(String(10))
    
    # Device information
    device = Column(String(255))
    os_version = Column(String(50))
    
    # Developer interaction
    developer_reply = Column(Text)
    developer_reply_date = Column(DateTime)
    
    # Additional metrics
    helpful_votes = Column(Integer, default=0)
    total_comment_count = Column(Integer, default=0)
    
    # Flags
    is_edited = Column(Boolean, default=False)
    is_top_developer = Column(Boolean, default=False)
    
    # Analysis fields
    tags = Column(String(500))  # Comma-separated tags
    category = Column(String(100))  # Feature request, bug report, etc.
    priority = Column(Integer)  # 1-5, with 1 being highest priority
    
    def __repr__(self):
        return f"<Review(id={self.id}, rating={self.rating}, date={self.review_date}>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'review_id': self.review_id,
            'source': self.source.value if self.source else None,
            'app_id': self.app_id,
            'app_version': self.app_version,
            'user_name': self.user_name,
            'rating': self.rating,
            'title': self.title,
            'content': self.content,
            'sentiment': self.sentiment.value if self.sentiment else None,
            'sentiment_score': self.sentiment_score,
            'review_date': self.review_date.isoformat() if self.review_date else None,
            'country': self.country,
            'language': self.language,
            'device': self.device,
            'os_version': self.os_version,
            'developer_reply': self.developer_reply,
            'developer_reply_date': self.developer_reply_date.isoformat() if self.developer_reply_date else None,
            'helpful_votes': self.helpful_votes,
            'total_comment_count': self.total_comment_count,
            'is_edited': self.is_edited,
            'is_top_developer': self.is_top_developer,
            'tags': self.tags,
            'category': self.category,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
