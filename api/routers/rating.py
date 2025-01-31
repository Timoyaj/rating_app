"""
API router for content rating endpoints.
"""
from typing import List, Optional
from datetime import datetime
import time
import uuid
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.database.session import get_db
from api.database import crud, models
from core.rating_service import RatingService
from core.file_processor import FileProcessor
from models.resource import Resource
from api.models.schemas import (
    ContentRequest,
    RatingResponse,
    BatchRatingRequest,
    BatchRatingResponse,
    SystemStats,
    ErrorResponse,
    ScoreResponse
)

router = APIRouter(prefix="/api/v1")

def get_rating_service():
    """Dependency injection for RatingService."""
    return RatingService(cache_dir=".cache")

def get_file_processor():
    """Dependency injection for FileProcessor."""
    return FileProcessor()

@router.post("/rate", response_model=RatingResponse, responses={400: {"model": ErrorResponse}})
async def rate_content(
    request: ContentRequest,
    rating_service: RatingService = Depends(get_rating_service),
    file_processor: FileProcessor = Depends(get_file_processor),
    db: Session = Depends(get_db)
):
    """Rate a single content resource."""
    try:
        start_time = time.time()

        # Process content based on file type
        file_type = request.file_type or file_processor.detect_file_type(request.content, request.metadata.dict())
        processed_content = file_processor.process_content(request.content, file_type)

        # Update request with processed content and file info
        request_with_processed = request.copy(update={
            'content': processed_content,
            'raw_content': request.content,
            'file_type': file_type
        })
        
        # Check if content already exists
        existing_content = crud.get_content_by_url(db, str(request.url))
        if existing_content:
            content = existing_content
        else:
            # Create new content in database
            content = crud.create_content(db, request_with_processed)
        
        # Convert request to Resource for rating
        resource = Resource(
            title=request.title,
            content=request.content,
            author=request.author,
            url=str(request.url),
            publication_date=request.publication_date.isoformat(),
            metadata=request.metadata.dict()
        )
        
        # Rate the resource
        rated_resource = rating_service.rate_resource(resource)
        
        # Store rating in database
        rating = crud.create_rating(
            db,
            content.id,
            RatingResponse(
                resource_id=rated_resource.resource_id,
                title=rated_resource.title,
                scores=ScoreResponse(**rated_resource.scores),
                final_score=rated_resource.final_score,
                rating_timestamp=rated_resource.last_rated,
                metadata=rated_resource.rating_metadata
            )
        )
        
        # Update system stats
        processing_time = time.time() - start_time
        crud.update_system_stats(
            db,
            (crud.get_system_stats(db) or models.SystemStat()).total_ratings + 1,
            rating_service.get_cache_stats(),
            processing_time
        )
        
        return RatingResponse(
            resource_id=rated_resource.resource_id,
            title=rated_resource.title,
            scores=ScoreResponse(**rated_resource.scores),
            final_score=rated_resource.final_score,
            rating_timestamp=rated_resource.last_rated,
            metadata=rated_resource.rating_metadata
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/rate-batch", response_model=BatchRatingResponse)
async def rate_batch(
    request: BatchRatingRequest,
    rating_service: RatingService = Depends(get_rating_service),
    file_processor: FileProcessor = Depends(get_file_processor),
    db: Session = Depends(get_db)
):
    """Rate multiple content resources in batch."""
    try:
        start_time = time.time()
        results = []
        
        for content_request in request.resources:
            # Process content based on file type
            file_type = content_request.file_type or file_processor.detect_file_type(
                content_request.content, 
                content_request.metadata.dict()
            )
            processed_content = file_processor.process_content(content_request.content, file_type)

            # Update request with processed content and file info
            request_with_processed = content_request.copy(update={
                'content': processed_content,
                'raw_content': content_request.content,
                'file_type': file_type
            })

            # Check if content exists
            existing_content = crud.get_content_by_url(db, str(content_request.url))
            if existing_content:
                content = existing_content
            else:
                # Create new content
                content = crud.create_content(db, request_with_processed)
            
            # Convert to Resource for rating
            resource = Resource(
                title=content_request.title,
                content=content_request.content,
                author=content_request.author,
                url=str(content_request.url),
                publication_date=content_request.publication_date.isoformat(),
                metadata=content_request.metadata.dict()
            )
            
            # Rate the resource
            rated_resource = rating_service.rate_resource(resource)
            
            # Store rating
            rating = crud.create_rating(
                db,
                content.id,
                RatingResponse(
                    resource_id=rated_resource.resource_id,
                    title=rated_resource.title,
                    scores=ScoreResponse(**rated_resource.scores),
                    final_score=rated_resource.final_score,
                    rating_timestamp=rated_resource.last_rated,
                    metadata=rated_resource.rating_metadata
                )
            )
            
            results.append(
                RatingResponse(
                    resource_id=rated_resource.resource_id,
                    title=rated_resource.title,
                    scores=ScoreResponse(**rated_resource.scores),
                    final_score=rated_resource.final_score,
                    rating_timestamp=rated_resource.last_rated,
                    metadata=rated_resource.rating_metadata
                )
            )
        
        processing_time = time.time() - start_time
        
        # Update system stats
        stats = crud.get_system_stats(db) or models.SystemStat()
        crud.update_system_stats(
            db,
            stats.total_ratings + len(results),
            rating_service.get_cache_stats(),
            processing_time
        )
        
        return BatchRatingResponse(
            results=results,
            total_processed=len(results),
            processing_time=processing_time,
            batch_id=str(uuid.uuid4())
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/ratings/{resource_id}", response_model=Optional[RatingResponse])
async def get_rating(
    resource_id: str,
    rating_service: RatingService = Depends(get_rating_service),
    db: Session = Depends(get_db)
):
    """Retrieve rating for a resource."""
    try:
        # Try database first
        db_rating = crud.get_rating(db, resource_id)
        if db_rating:
            return RatingResponse(
                resource_id=db_rating.resource_id,
                title=db_rating.content.title,
                scores=ScoreResponse(
                    relevance=db_rating.relevance_score,
                    authority=db_rating.authority_score,
                    engagement=db_rating.engagement_score,
                    clarity=db_rating.clarity_score,
                    impact=db_rating.impact_score
                ),
                final_score=db_rating.final_score,
                rating_timestamp=db_rating.rating_timestamp,
                metadata=db_rating.rating_metadata
            )
        
        # Fall back to cache
        cached = rating_service.get_cached_rating(resource_id)
        if not cached:
            return JSONResponse(
                status_code=404,
                content={"message": f"No rating found for resource {resource_id}"}
            )
            
        return RatingResponse(
            resource_id=cached.resource_id,
            title=cached.title,
            scores=ScoreResponse(**cached.scores),
            final_score=cached.final_score,
            rating_timestamp=cached.last_rated,
            metadata=cached.rating_metadata
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get("/stats", response_model=SystemStats)
async def get_stats(
    rating_service: RatingService = Depends(get_rating_service),
    db: Session = Depends(get_db)
):
    """Get system statistics."""
    try:
        stats = crud.get_system_stats(db)
        
        if not stats:
            stats = models.SystemStat(
                total_ratings=0,
                cache_stats=rating_service.get_cache_stats(),
                avg_processing_time=0.0,
                active_since=datetime.utcnow()
            )
            db.add(stats)
            db.commit()
        
        return SystemStats(
            total_ratings=stats.total_ratings,
            cache_stats=stats.cache_stats,
            avg_processing_time=stats.avg_processing_time,
            active_since=stats.active_since
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
