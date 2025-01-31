"""
Pydantic models for API request/response schemas.
"""
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

class Metadata(BaseModel):
    """Schema for content metadata."""
    keywords: List[str] = Field(..., description="List of content keywords")
    category: str = Field(..., description="Content category")
    language: str = Field(..., description="Content language code")
    view_count: int = Field(0, description="Number of views")
    avg_interaction_time: float = Field(0.0, description="Average interaction time in seconds")
    social_shares: int = Field(0, description="Number of social media shares")
    total_interactions: int = Field(0, description="Total number of user interactions")
    citations: int = Field(0, description="Number of citations")
    author_credentials_score: float = Field(0.0, description="Author expertise score (0-10)")
    domain_authority: float = Field(0.0, description="Domain authority score")
    positive_outcomes: int = Field(0, description="Number of positive outcomes")
    conversion_rate: float = Field(0.0, description="Conversion rate")
    user_satisfaction: float = Field(0.0, description="User satisfaction score (0-10)")
    review_count: int = Field(0, description="Number of reviews")
    file_type: Optional[str] = Field(None, description="Type of file (pdf, html, docx, txt, md)")

class ContentRequest(BaseModel):
    """Schema for content rating request."""
    title: str = Field(..., description="Content title")
    content: str = Field(..., description="Content text (may be base64 encoded for binary formats)")
    author: str = Field(..., description="Content author")
    url: HttpUrl = Field(..., description="Content URL")
    publication_date: datetime = Field(..., description="Publication date")
    metadata: Metadata = Field(..., description="Content metadata")
    file_type: Optional[str] = Field(None, description="Type of file (pdf, html, docx, txt, md)")
    raw_content: Optional[str] = Field(None, description="Original raw content before processing")

class ScoreResponse(BaseModel):
    """Schema for individual criterion scores."""
    relevance: float = Field(..., description="Relevance score (0-10)")
    authority: float = Field(..., description="Authority score (0-10)")
    engagement: float = Field(..., description="Engagement score (0-10)")
    clarity: float = Field(..., description="Clarity score (0-10)")
    impact: float = Field(..., description="Impact score (0-10)")

class RatingResponse(BaseModel):
    """Schema for rating response."""
    resource_id: str = Field(..., description="Unique resource identifier")
    title: str = Field(..., description="Content title")
    scores: ScoreResponse = Field(..., description="Individual criterion scores")
    final_score: float = Field(..., description="Final calculated score (0-10)")
    rating_timestamp: datetime = Field(..., description="Rating calculation timestamp")
    metadata: Dict = Field(..., description="Rating metadata")

class BatchRatingRequest(BaseModel):
    """Schema for batch rating request."""
    resources: List[ContentRequest] = Field(..., description="List of content resources to rate")
    batch_size: Optional[int] = Field(10, description="Batch processing size")

class BatchRatingResponse(BaseModel):
    """Schema for batch rating response."""
    results: List[RatingResponse] = Field(..., description="List of rating results")
    total_processed: int = Field(..., description="Total number of resources processed")
    processing_time: float = Field(..., description="Total processing time in seconds")
    batch_id: str = Field(..., description="Unique batch identifier")

class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

class SystemStats(BaseModel):
    """Schema for system statistics."""
    total_ratings: int = Field(..., description="Total number of ratings processed")
    cache_stats: Dict = Field(..., description="Cache statistics")
    avg_processing_time: float = Field(..., description="Average processing time per rating")
    active_since: datetime = Field(..., description="System start timestamp")
