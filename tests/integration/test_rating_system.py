"""
Integration tests for the complete rating system.
"""
import pytest
from datetime import datetime
import json
import os

from core.rating_service import RatingService
from models.resource import Resource

@pytest.mark.integration
class TestRatingSystem:
    """Integration test suite for the complete rating system."""

    def test_complete_rating_workflow(self, rating_service, sample_resource):
        """Test the complete workflow of rating a resource."""
        # Rate the resource
        rated_resource = rating_service.rate_resource(sample_resource)
        
        # Verify all scores were calculated
        assert rated_resource.scores.get('relevance') is not None
        assert rated_resource.scores.get('authority') is not None
        assert rated_resource.scores.get('engagement') is not None
        assert rated_resource.scores.get('clarity') is not None
        assert rated_resource.scores.get('impact') is not None
        
        # Verify final score
        assert rated_resource.final_score is not None
        assert 1.0 <= rated_resource.final_score <= 10.0
        
        # Verify rating metadata
        assert 'calculation_timestamp' in rated_resource.rating_metadata
        assert 'score_breakdown' in rated_resource.rating_metadata
        
        # Verify caching
        cached_resource = rating_service.get_cached_rating(rated_resource.resource_id)
        assert cached_resource is not None
        assert cached_resource.final_score == rated_resource.final_score

    def test_batch_processing_workflow(self, rating_service, sample_batch_resources):
        """Test batch processing of multiple resources."""
        # Process batch
        rated_resources = rating_service.bulk_rate_resources(sample_batch_resources)
        
        # Verify all resources were rated
        assert len(rated_resources) == len(sample_batch_resources)
        
        # Verify each resource has complete ratings
        for resource in rated_resources:
            assert len(resource.scores) == 5  # All 5 criteria
            assert resource.final_score is not None
            assert resource.last_rated is not None
            
        # Verify scores are different (showing customization)
        scores = [r.final_score for r in rated_resources]
        assert len(set(scores)) > 1  # At least some scores should be different

    def test_cache_persistence(self, temp_cache_dir, sample_resource):
        """Test that ratings persist across service restarts."""
        # Create service and rate resource
        service1 = RatingService(cache_dir=temp_cache_dir)
        rated_resource = service1.rate_resource(sample_resource)
        original_score = rated_resource.final_score
        
        # Create new service instance
        service2 = RatingService(cache_dir=temp_cache_dir)
        cached_resource = service2.get_cached_rating(rated_resource.resource_id)
        
        # Verify scores match
        assert cached_resource is not None
        assert cached_resource.final_score == original_score

    @pytest.mark.slow
    def test_performance_with_large_content(self, rating_service):
        """Test system performance with large content."""
        # Create resource with large content
        large_content = "lorem ipsum " * 1000  # Approximately 10KB of text
        large_resource = Resource(
            title="Large Resource",
            content=large_content,
            author="Test Author",
            url="https://example.com/large",
            publication_date=datetime.now().isoformat(),
            metadata={
                'keywords': ['test', 'large', 'content'],
                'category': 'testing',
                'language': 'en',
                'view_count': 1000,
                'avg_interaction_time': 300,
                'social_shares': 150,
                'total_interactions': 500,
                'citations': 25,
                'author_credentials_score': 8.0,
                'domain_authority': 70,
                'positive_outcomes': 7,
                'conversion_rate': 0.12,
                'user_satisfaction': 8.5,
                'review_count': 250
            }
        )
        
        # Time the rating process
        import time
        start_time = time.time()
        rated_resource = rating_service.rate_resource(large_resource)
        processing_time = time.time() - start_time
        
        # Verify reasonable performance
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert rated_resource.final_score is not None

    def test_error_handling(self, rating_service):
        """Test system error handling with invalid data."""
        # Test with missing required fields
        invalid_resource = Resource(
            title="Invalid Resource",
            content="",  # Empty content
            author="",   # Empty author
            url="not-a-valid-url",  # Invalid URL
            publication_date="invalid-date",  # Invalid date
            metadata={}  # Missing required metadata
        )
        
        with pytest.raises(ValueError):
            rating_service.rate_resource(invalid_resource)

    def test_data_consistency(self, rating_service, sample_resource):
        """Test consistency of ratings across multiple calculations."""
        # Rate the same resource multiple times
        results = []
        for _ in range(3):
            rated = rating_service.rate_resource(sample_resource, force_refresh=True)
            results.append(rated.final_score)
        
        # Verify consistent results
        assert len(set(results)) == 1  # All scores should be identical

    def test_metadata_handling(self, rating_service, sample_resource):
        """Test handling of various metadata scenarios."""
        # Modify metadata incrementally
        modifications = [
            {'view_count': 2000},
            {'social_shares': 300},
            {'author_credentials_score': 9.0},
            {'citations': 50}
        ]
        
        scores = []
        for mod in modifications:
            sample_resource.metadata.update(mod)
            rated = rating_service.rate_resource(sample_resource, force_refresh=True)
            scores.append(rated.final_score)
        
        # Verify scores reflect metadata changes
        assert len(set(scores)) > 1  # Scores should vary with metadata changes

    def test_system_recovery(self, rating_service, sample_resource, temp_cache_dir):
        """Test system recovery from cache corruption."""
        # Rate resource normally
        original = rating_service.rate_resource(sample_resource)
        
        # Corrupt cache file
        cache_file = os.path.join(temp_cache_dir, f"{original.resource_id}.json")
        with open(cache_file, 'w') as f:
            f.write("corrupted data")
        
        # System should handle corruption gracefully
        recovered = rating_service.rate_resource(sample_resource)
        assert recovered.final_score is not None
