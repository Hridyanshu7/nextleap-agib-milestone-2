from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment or use SQLite as default
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///reviews.db')

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Create base class for models
Base = declarative_base()

class BaseModel:
    """Base model with common columns and methods"""
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def save(self):
        """Save the current model to the database"""
        try:
            db = SessionLocal()
            db.add(self)
            db.commit()
            db.refresh(self)
            return self
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving to database: {str(e)}")
            raise
        finally:
            db.close()
    
    def delete(self):
        """Delete the current model from the database"""
        try:
            db = SessionLocal()
            db.delete(self)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting from database: {str(e)}")
            return False
        finally:
            db.close()

# Create database tables
def init_db():
    """Initialize the database and create tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

# Dependency to get DB session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
