"""
Main rating service that orchestrates the content rating process.
"""
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging

from models.resource import Resource
from core.rating_calculator import RatingCalculator
from core.metrics_collector import MetricsCollector
from core.data_processor import DataProcessor
from utils.cache_manager import CacheManager

class RatingService:
    """Main service for rating content resources."""

    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize rating service with required components.
        
        Args:
            cache_dir: Directory for caching results
        """
        self.calculator = RatingCalculator()
        self.metrics_collector = MetricsCollector()
        self.data_processor = DataProcessor()
        self.cache_manager = CacheManager(cache_dir=cache_dir)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def rate_resource(self, resource_data: Union[Dict[str, any], Resource],
                     force_refresh: bool = False) -> Resource:
        """
        Rate a content resource.
        
        Args:
            resource_data: Dictionary containing resource data or Resource instance
            force_refresh: Force recalculation even if cached
            
        Returns:
            Resource: Rated resource with scores
        """
        # Convert dict to Resource if needed
        resource = (resource_data if isinstance(resource_data, Resource)
                   else Resource.from_dict(resource_data))
        
        # Check cache first unless force refresh
        if not force_refresh:
            cached_result = self.cache_manager.get(resource.resource_id)
            if cached_result and not Resource.from_dict(cached_result).is_stale():
                self.logger.info(f"Retrieved cached rating for resource {resource.resource_id}")
                return Resource.from_dict(cached_result)

        try:
            # Validate and process data
            errors = self.data_processor.validate_resource_data(resource.to_dict())
            if errors:
                raise ValueError(f"Invalid resource data: {errors}")
            
            processed_data = self.data_processor.prepare_resource_data(resource.to_dict())
            resource = Resource.from_dict(processed_data)
            
            # Collect and analyze metrics
            self._collect_metrics(resource)
            
            # Calculate final rating
            self._calculate_rating(resource)
            
            # Cache results
            self.cache_manager.set(resource.resource_id, resource.to_dict())
            
            self.logger.info(f"Successfully rated resource {resource.resource_id}")
            return resource
            
        except Exception as e:
            self.logger.error(f"Error rating resource: {str(e)}")
            raise

    def _collect_metrics(self, resource: Resource) -> None:
        """
        Collect all required metrics for rating.
        
        Args:
            resource: Resource to collect metrics for
        """
        try:
            # Analyze text content
            content_metrics = self.metrics_collector.analyze_text_content(resource.content)
            
            # Collect engagement metrics
            engagement_metrics = self.metrics_collector.analyze_engagement_metrics({
                'view_count': resource.metadata.get('view_count', 0),
                'interaction_time': resource.metadata.get('avg_interaction_time', 0),
                'social_shares': resource.metadata.get('social_shares', 0),
                'interactions': resource.metadata.get('total_interactions', 0)
            })
            
            # Collect authority metrics
            authority_metrics = self.metrics_collector.analyze_authority_metrics({
                'citations': resource.metadata.get('citations', 0),
                'author_credentials': resource.metadata.get('author_credentials_score', 0),
                'domain_authority': resource.metadata.get('domain_authority', 0)
            })
            
            # Collect impact metrics
            impact_metrics = self.metrics_collector.calculate_impact_metrics({
                'positive_outcomes': resource.metadata.get('positive_outcomes', 0),
                'conversion_rate': resource.metadata.get('conversion_rate', 0),
                'user_satisfaction': resource.metadata.get('user_satisfaction', 0)
            })
            
            # Store metrics in resource metadata
            resource.rating_metadata.update({
                'content_metrics': content_metrics,
                'engagement_metrics': engagement_metrics,
                'authority_metrics': authority_metrics,
                'impact_metrics': impact_metrics
            })
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {str(e)}")
            raise

    def _calculate_rating(self, resource: Resource) -> None:
        """
        Calculate final rating scores.
        
        Args:
            resource: Resource to calculate rating for
        """
        try:
            metrics = resource.rating_metadata
            
            # Calculate individual scores
            relevance_score = self.calculator.calculate_relevance(
                len(metrics['content_metrics']['keywords']),
                metrics['content_metrics']['word_count']
            )
            
            authority_score = self.calculator.calculate_authority(
                metrics['authority_metrics']['citation_impact'],
                metrics['authority_metrics']['author_expertise'],
                10.0  # Max authority score
            )
            
            engagement_score = self.calculator.calculate_engagement(
                metrics['engagement_metrics']['interaction_rate'],
                metrics['engagement_metrics']['avg_session_time'],
                metrics['engagement_metrics']['social_impact'],
                10.0  # Max engagement score
            )
            
            clarity_score = self.calculator.calculate_clarity(
                metrics['content_metrics']['readability_score'],
                len(metrics['content_metrics']['keywords']),
                True,  # Assuming has_cta for now
                10.0  # Max clarity score
            )
            
            impact_score = self.calculator.calculate_impact(
                metrics['impact_metrics']['outcome_effectiveness'],
                metrics['impact_metrics']['conversion_impact'],
                10.0  # Max impact score
            )
            
            # Update individual scores
            scores = {
                'relevance': relevance_score,
                'authority': authority_score,
                'engagement': engagement_score,
                'clarity': clarity_score,
                'impact': impact_score
            }
            
            for criterion, score in scores.items():
                resource.update_score(criterion, score)
            
            # Calculate final score
            review_count = resource.metadata.get('review_count', 0)
            final_score = self.calculator.calculate_final_score(scores, review_count)
            
            # Update final score with metadata
            resource.set_final_score(final_score, {
                'calculation_timestamp': datetime.now().isoformat(),
                'review_count': review_count,
                'score_breakdown': scores
            })
            
        except Exception as e:
            self.logger.error(f"Error calculating rating: {str(e)}")
            raise

    def bulk_rate_resources(self, resources: List[Union[Dict[str, any], Resource]],
                          batch_size: int = 10) -> List[Resource]:
        """
        Rate multiple resources in batches.
        
        Args:
            resources: List of resource data or Resource instances
            batch_size: Number of resources to process in each batch
            
        Returns:
            List[Resource]: List of rated resources
        """
        rated_resources = []
        
        for i in range(0, len(resources), batch_size):
            batch = resources[i:i + batch_size]
            
            try:
                # Process batch
                for resource_data in batch:
                    rated_resource = self.rate_resource(resource_data)
                    rated_resources.append(rated_resource)
                    
                self.logger.info(f"Processed batch {i//batch_size + 1}")
                
            except Exception as e:
                self.logger.error(f"Error processing batch: {str(e)}")
                continue
                
        return rated_resources

    def get_cached_rating(self, resource_id: str) -> Optional[Resource]:
        """
        Retrieve cached rating for a resource.
        
        Args:
            resource_id: Resource identifier
            
        Returns:
            Optional[Resource]: Cached resource if available
        """
        cached_data = self.cache_manager.get(resource_id)
        if cached_data:
            return Resource.from_dict(cached_data)
        return None

    def clear_rating_cache(self) -> None:
        """Clear all cached ratings."""
        self.cache_manager.clear_cache()
        self.logger.info("Cleared rating cache")

    def get_cache_stats(self) -> Dict[str, any]:
        """
        Get cache statistics.
        
        Returns:
            Dict containing cache statistics
        """
        return self.cache_manager.get_cache_stats()
