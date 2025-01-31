"""
SQLAlchemy database models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .session import Base

class Content(Base):
    """Content resource database model."""
    __tablename__ = "content_resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    raw_content = Column(String)  # Original file content
    file_type = Column(String)    # Type of file (pdf, html, docx, txt, md)
    author = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    publication_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    content_metadata = relationship("ContentMetadata", back_populates="content", uselist=False)
    ratings = relationship("Rating", back_populates="content")

class ContentMetadata(Base):
    """Content metadata database model."""
    __tablename__ = "content_metadata"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content_resources.id"))
    keywords = Column(JSON)  # List of strings
    category = Column(String, index=True)
    language = Column(String)
    view_count = Column(Integer, default=0)
    avg_interaction_time = Column(Float, default=0.0)
    social_shares = Column(Integer, default=0)
    total_interactions = Column(Integer, default=0)
    citations = Column(Integer, default=0)
    author_credentials_score = Column(Float, default=0.0)
    domain_authority = Column(Float, default=0.0)
    positive_outcomes = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    user_satisfaction = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    
    # Relationships
    content = relationship("Content", back_populates="content_metadata")

class Rating(Base):
    """Content rating database model."""
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content_resources.id"))
    resource_id = Column(String, unique=True, index=True)
    final_score = Column(Float)
    rating_timestamp = Column(DateTime, default=datetime.utcnow)
    rating_metadata = Column(JSON)  # Additional rating metadata
    
    # Individual scores
    relevance_score = Column(Float)
    authority_score = Column(Float)
    engagement_score = Column(Float)
    clarity_score = Column(Float)
    impact_score = Column(Float)
    
    # Relationships
    content = relationship("Content", back_populates="ratings")

class SystemStat(Base):
    """System statistics database model."""
    __tablename__ = "system_stats"

    id = Column(Integer, primary_key=True, index=True)
    total_ratings = Column(Integer, default=0)
    cache_stats = Column(JSON)
    avg_processing_time = Column(Float, default=0.0)
    active_since = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
