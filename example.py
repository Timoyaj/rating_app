"""
Example usage of the content rating system.
"""
from core.rating_service import RatingService
from models.resource import Resource
import json

def main():
    """Demonstrate the content rating system with example resources."""
    
    # Initialize rating service
    rating_service = RatingService(cache_dir=".cache")
    
    # Example resource data
    example_resource = {
        'title': 'Guide to Corporate Sponsorships',
        'content': '''
        Corporate sponsorships can be a valuable source of funding for nonprofits.
        This comprehensive guide explores strategies for identifying, approaching,
        and securing corporate sponsors. Learn how to create compelling
        partnership proposals, measure impact, and build long-term relationships
        with sponsors. Includes case studies, templates, and best practices.
        ''',
        'author': 'Jane Smith',
        'url': 'https://example.com/guide-corporate-sponsorships',
        'publication_date': '2024-01-30T00:00:00Z',
        'metadata': {
            'keywords': [
                'corporate sponsorship',
                'nonprofit funding',
                'partnership',
                'fundraising',
                'sponsorship proposals'
            ],
            'category': 'nonprofit-management',
            'language': 'en',
            'view_count': 1500,
            'avg_interaction_time': 420,  # 7 minutes
            'social_shares': 250,
            'total_interactions': 800,
            'citations': 45,
            'author_credentials_score': 8.5,
            'domain_authority': 75,
            'positive_outcomes': 8,
            'conversion_rate': 0.15,
            'user_satisfaction': 9.2,
            'review_count': 520
        }
    }

    try:
        # Rate single resource
        print("\nRating single resource...")
        rated_resource = rating_service.rate_resource(example_resource)
        
        # Print results
        print("\nRating Results:")
        print("-" * 50)
        print(f"Resource: {rated_resource.title}")
        print(f"Author: {rated_resource.author}")
        print("\nIndividual Scores:")
        for criterion, score in rated_resource.scores.items():
            print(f"{criterion.capitalize()}: {score:.2f}")
        print(f"\nFinal Score: {rated_resource.final_score:.2f}")
        
        # Print detailed metrics
        print("\nDetailed Metrics:")
        print("-" * 50)
        print(json.dumps(rated_resource.rating_metadata, indent=2))
        
        # Demonstrate caching
        print("\nTesting cache...")
        cached_resource = rating_service.get_cached_rating(rated_resource.resource_id)
        if cached_resource:
            print("Successfully retrieved from cache")
            print(f"Cached Score: {cached_resource.final_score:.2f}")
        
        # Demonstrate batch processing
        print("\nTesting batch processing...")
        # Create variations of the example resource
        batch_resources = []
        for i in range(3):
            resource_copy = dict(example_resource)
            resource_copy['title'] = f"Resource Version {i+1}"
            resource_copy['metadata'] = dict(example_resource['metadata'])
            resource_copy['metadata']['view_count'] += i * 100
            batch_resources.append(resource_copy)
        
        rated_batch = rating_service.bulk_rate_resources(batch_resources)
        print(f"Successfully rated {len(rated_batch)} resources in batch")
        
        # Print batch results
        print("\nBatch Results:")
        print("-" * 50)
        for resource in rated_batch:
            print(f"{resource.title}: {resource.final_score:.2f}")
        
        # Show cache statistics
        print("\nCache Statistics:")
        print("-" * 50)
        cache_stats = rating_service.get_cache_stats()
        print(json.dumps(cache_stats, indent=2))

    except Exception as e:
        print(f"Error in example: {str(e)}")

if __name__ == "__main__":
    main()
