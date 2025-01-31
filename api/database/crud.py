"""
CRUD operations for database models.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from . import models
from api.models import schemas

def create_content(db: Session, content: schemas.ContentRequest) -> models.Content:
    """Create a new content resource."""
    db_content = models.Content(
        title=content.title,
        content=content.content,
        raw_content=content.raw_content,
        file_type=content.file_type,
        author=content.author,
        url=str(content.url),
        publication_date=content.publication_date
    )
    
    # Create metadata
    db_metadata = models.ContentMetadata(
        keywords=content.metadata.keywords,
        category=content.metadata.category,
        language=content.metadata.language,
        view_count=content.metadata.view_count,
        avg_interaction_time=content.metadata.avg_interaction_time,
        social_shares=content.metadata.social_shares,
        total_interactions=content.metadata.total_interactions,
        citations=content.metadata.citations,
        author_credentials_score=content.metadata.author_credentials_score,
        domain_authority=content.metadata.domain_authority,
        positive_outcomes=content.metadata.positive_outcomes,
        conversion_rate=content.metadata.conversion_rate,
        user_satisfaction=content.metadata.user_satisfaction,
        review_count=content.metadata.review_count
    )
    
    db_content.content_metadata = db_metadata
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

def get_content(db: Session, content_id: int) -> Optional[models.Content]:
    """Get content by ID."""
    return db.query(models.Content).filter(models.Content.id == content_id).first()

def get_content_by_url(db: Session, url: str) -> Optional[models.Content]:
    """Get content by URL."""
    return db.query(models.Content).filter(models.Content.url == url).first()

def create_rating(
    db: Session, content_id: int, rating: schemas.RatingResponse
) -> models.Rating:
    """Create a new rating."""
    db_rating = models.Rating(
        content_id=content_id,
        resource_id=rating.resource_id,
        final_score=rating.final_score,
        rating_timestamp=rating.rating_timestamp,
        rating_metadata=rating.metadata,
        relevance_score=rating.scores.relevance,
        authority_score=rating.scores.authority,
        engagement_score=rating.scores.engagement,
        clarity_score=rating.scores.clarity,
        impact_score=rating.scores.impact
    )
    
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

def get_rating(db: Session, resource_id: str) -> Optional[models.Rating]:
    """Get rating by resource ID."""
    return db.query(models.Rating).filter(models.Rating.resource_id == resource_id).first()

def get_content_ratings(db: Session, content_id: int) -> List[models.Rating]:
    """Get all ratings for a content resource."""
    return db.query(models.Rating).filter(models.Rating.content_id == content_id).all()

def update_system_stats(
    db: Session,
    total_ratings: int,
    cache_stats: dict,
    avg_processing_time: float
) -> models.SystemStat:
    """Update system statistics."""
    stats = db.query(models.SystemStat).first()
    
    if not stats:
        stats = models.SystemStat(
            total_ratings=total_ratings,
            cache_stats=cache_stats,
            avg_processing_time=avg_processing_time,
            active_since=datetime.utcnow()
        )
        db.add(stats)
    else:
        stats.total_ratings = total_ratings
        stats.cache_stats = cache_stats
        stats.avg_processing_time = avg_processing_time
    
    db.commit()
    db.refresh(stats)
    return stats

def get_system_stats(db: Session) -> Optional[models.SystemStat]:
    """Get current system statistics."""
    return db.query(models.SystemStat).first()
