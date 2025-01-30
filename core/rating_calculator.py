"""
Core rating calculator implementation for the content optimization system.
"""
from typing import Dict, List, Union
import numpy as np

class RatingCalculator:
    """Main class for calculating overall ratings based on multiple criteria."""
    
    # Weight distribution as per specifications
    WEIGHTS = {
        'relevance': 0.25,
        'authority': 0.20,
        'engagement': 0.20,
        'clarity': 0.15,
        'impact': 0.20
    }

    def __init__(self):
        self.validate_weights()

    def validate_weights(self) -> None:
        """Validate that weights sum to 1."""
        if abs(sum(self.WEIGHTS.values()) - 1.0) > 0.0001:
            raise ValueError("Weights must sum to 1")

    def calculate_relevance(self, matched_keywords: int, total_keywords: int) -> float:
        """
        Calculate relevance score based on keyword matching.
        
        Args:
            matched_keywords: Number of matched keywords
            total_keywords: Total number of keywords in resource
            
        Returns:
            float: Relevance score (1-10)
        """
        if total_keywords == 0:
            return 0.0
        return min(10.0, (matched_keywords / total_keywords) * 10)

    def calculate_authority(self, citations: int, credentials_score: float, 
                          max_authority: float) -> float:
        """
        Calculate authority score based on citations and credentials.
        
        Args:
            citations: Number of citations
            credentials_score: Score based on author credentials (0-10)
            max_authority: Maximum possible authority score
            
        Returns:
            float: Authority score (1-10)
        """
        if max_authority <= 0:
            return 0.0
        raw_score = (citations + credentials_score) / max_authority
        return min(10.0, raw_score * 10)

    def calculate_engagement(self, interactions: int, session_time: float,
                           social_shares: int, max_engagement: float) -> float:
        """
        Calculate engagement score based on user interactions.
        
        Args:
            interactions: Number of user interactions
            session_time: Average session time in minutes
            social_shares: Number of social media shares
            max_engagement: Maximum possible engagement score
            
        Returns:
            float: Engagement score (1-10)
        """
        if max_engagement <= 0:
            return 0.0
        total_engagement = interactions + (session_time * 2) + social_shares
        return min(10.0, (total_engagement / max_engagement) * 10)

    def calculate_clarity(self, readability_score: float, usability_features: int,
                         has_cta: bool, max_clarity: float) -> float:
        """
        Calculate clarity score based on readability and usability.
        
        Args:
            readability_score: Flesch Reading Score (0-100)
            usability_features: Count of usability features
            has_cta: Whether clear call-to-action exists
            max_clarity: Maximum possible clarity score
            
        Returns:
            float: Clarity score (1-10)
        """
        if max_clarity <= 0:
            return 0.0
        normalized_readability = readability_score / 100.0
        cta_score = 1 if has_cta else 0
        total_clarity = (normalized_readability * 5) + (usability_features * 0.5) + cta_score
        return min(10.0, (total_clarity / max_clarity) * 10)

    def calculate_impact(self, positive_outcomes: int, tangible_metrics: float,
                        max_impact: float) -> float:
        """
        Calculate impact score based on outcomes and metrics.
        
        Args:
            positive_outcomes: Number of positive outcomes
            tangible_metrics: Score based on tangible metrics (0-10)
            max_impact: Maximum possible impact score
            
        Returns:
            float: Impact score (1-10)
        """
        if max_impact <= 0:
            return 0.0
        total_impact = positive_outcomes + tangible_metrics
        return min(10.0, (total_impact / max_impact) * 10)

    def apply_modifiers(self, scores: Dict[str, float]) -> float:
        """
        Apply bonus and penalty modifiers to the final score.
        
        Args:
            scores: Dictionary of individual criterion scores
            
        Returns:
            float: Modifier value to add to final score
        """
        modifier = 0.0
        
        # Apply bonus for exceptional performance
        if any(score >= 9.5 for score in scores.values()):
            modifier += 0.5
            
        # Apply penalty for severe shortcomings
        if any(score <= 3.0 for score in scores.values()):
            modifier -= 0.5
            
        return modifier

    def calculate_final_score(self, scores: Dict[str, float], 
                            review_count: int = 0) -> float:
        """
        Calculate final score with weights and modifiers.
        
        Args:
            scores: Dictionary of individual criterion scores
            review_count: Number of reviews/data points
            
        Returns:
            float: Final adjusted score (1-10)
        """
        # Validate input scores
        required_criteria = set(self.WEIGHTS.keys())
        if not all(criterion in scores for criterion in required_criteria):
            raise ValueError(f"Missing required criteria. Expected: {required_criteria}")

        # Calculate weighted sum
        weighted_score = sum(
            scores[criterion] * weight 
            for criterion, weight in self.WEIGHTS.items()
        )

        # Apply modifiers
        modifier = self.apply_modifiers(scores)
        
        # Apply statistical significance adjustment
        if review_count >= 500:
            modifier += 0.2

        return min(10.0, max(1.0, weighted_score + modifier))
