"""
API router for content rating endpoints.
"""
from typing import List, Optional
from datetime import datetime
import time
import uuid
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from core.rating_service import RatingService
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

# In-memory stats (for demo - should use proper storage in production)
system_stats = {
    "total_ratings": 0,
    "start_time": datetime.now(),
    "processing_times": []
}

def get_rating_service():
    """Dependency injection for RatingService."""
    return RatingService(cache_dir=".cache")

@router.post("/rate", response_model=RatingResponse, responses={400: {"model": ErrorResponse}})
async def rate_content(
    request: ContentRequest,
    rating_service: RatingService = Depends(get_rating_service)
):
    """
    Rate a single content resource.
    
    Args:
        request: Content resource data
        rating_service: Injected RatingService instance
        
    Returns:
        RatingResponse: Rating results
    """
    try:
        start_time = time.time()
        
        # Convert request to Resource
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
        
        # Update stats
        processing_time = time.time() - start_time
        system_stats["total_ratings"] += 1
        system_stats["processing_times"].append(processing_time)
        
        # Convert to response schema
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
    rating_service: RatingService = Depends(get_rating_service)
):
    """
    Rate multiple content resources in batch.
    
    Args:
        request: Batch of content resources
        rating_service: Injected RatingService instance
        
    Returns:
        BatchRatingResponse: Batch rating results
    """
    try:
        start_time = time.time()
        
        # Convert requests to Resources
        resources = [
            Resource(
                title=item.title,
                content=item.content,
                author=item.author,
                url=str(item.url),
                publication_date=item.publication_date.isoformat(),
                metadata=item.metadata.dict()
            )
            for item in request.resources
        ]
        
        # Process batch
        rated_resources = rating_service.bulk_rate_resources(
            resources,
            batch_size=request.batch_size
        )
        
        # Convert to response schemas
        results = [
            RatingResponse(
                resource_id=resource.resource_id,
                title=resource.title,
                scores=ScoreResponse(**resource.scores),
                final_score=resource.final_score,
                rating_timestamp=resource.last_rated,
                metadata=resource.rating_metadata
            )
            for resource in rated_resources
        ]
        
        processing_time = time.time() - start_time
        
        # Update stats
        system_stats["total_ratings"] += len(results)
        system_stats["processing_times"].append(processing_time)
        
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
    rating_service: RatingService = Depends(get_rating_service)
):
    """
    Retrieve cached rating for a resource.
    
    Args:
        resource_id: Resource identifier
        rating_service: Injected RatingService instance
        
    Returns:
        Optional[RatingResponse]: Cached rating if available
    """
    try:
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
    rating_service: RatingService = Depends(get_rating_service)
):
    """
    Get system statistics.
    
    Args:
        rating_service: Injected RatingService instance
        
    Returns:
        SystemStats: Current system statistics
    """
    try:
        cache_stats = rating_service.get_cache_stats()
        avg_time = (
            sum(system_stats["processing_times"]) / len(system_stats["processing_times"])
            if system_stats["processing_times"]
            else 0
        )
        
        return SystemStats(
            total_ratings=system_stats["total_ratings"],
            cache_stats=cache_stats,
            avg_processing_time=avg_time,
            active_since=system_stats["start_time"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
