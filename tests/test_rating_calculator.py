"""
Unit tests for the RatingCalculator component.
"""
import pytest
from core.rating_calculator import RatingCalculator

@pytest.fixture
def calculator():
    """Fixture providing a RatingCalculator instance."""
    return RatingCalculator()

def test_weight_validation(calculator):
    """Test that weights sum to 1."""
    total_weight = sum(calculator.WEIGHTS.values())
    assert abs(total_weight - 1.0) < 0.0001

def test_relevance_calculation(calculator):
    """Test relevance score calculation."""
    # Perfect match
    assert calculator.calculate_relevance(10, 10) == 10.0
    
    # No matches
    assert calculator.calculate_relevance(0, 10) == 0.0
    
    # Half matches
    assert calculator.calculate_relevance(5, 10) == 5.0
    
    # No keywords
    assert calculator.calculate_relevance(0, 0) == 0.0
    
    # More matches than total (should cap at 10)
    assert calculator.calculate_relevance(15, 10) == 10.0

def test_authority_calculation(calculator):
    """Test authority score calculation."""
    # Perfect score
    assert calculator.calculate_authority(5, 5, 10) == 10.0
    
    # Zero authority
    assert calculator.calculate_authority(0, 0, 10) == 0.0
    
    # Mid-range score
    assert calculator.calculate_authority(3, 2, 10) == 5.0
    
    # Invalid max authority
    assert calculator.calculate_authority(5, 5, 0) == 0.0
    
    # Score capped at 10
    assert calculator.calculate_authority(15, 15, 10) == 10.0

def test_engagement_calculation(calculator):
    """Test engagement score calculation."""
    # High engagement
    assert calculator.calculate_engagement(100, 10, 50, 20) == 10.0
    
    # No engagement
    assert calculator.calculate_engagement(0, 0, 0, 10) == 0.0
    
    # Mid-range engagement
    engagement = calculator.calculate_engagement(50, 5, 25, 20)
    assert 0 < engagement < 10
    
    # Invalid max engagement
    assert calculator.calculate_engagement(100, 10, 50, 0) == 0.0

def test_clarity_calculation(calculator):
    """Test clarity score calculation."""
    # Perfect clarity
    assert calculator.calculate_clarity(100, 10, True, 10) == 10.0
    
    # Poor clarity
    assert calculator.calculate_clarity(0, 0, False, 10) == 0.0
    
    # Mid-range clarity
    clarity = calculator.calculate_clarity(50, 5, True, 10)
    assert 0 < clarity < 10
    
    # Invalid max clarity
    assert calculator.calculate_clarity(100, 10, True, 0) == 0.0

def test_impact_calculation(calculator):
    """Test impact score calculation."""
    # High impact
    assert calculator.calculate_impact(5, 5, 10) == 10.0
    
    # No impact
    assert calculator.calculate_impact(0, 0, 10) == 0.0
    
    # Mid-range impact
    assert calculator.calculate_impact(2, 3, 10) == 5.0
    
    # Invalid max impact
    assert calculator.calculate_impact(5, 5, 0) == 0.0

def test_modifier_application(calculator):
    """Test score modifier application."""
    # Test bonus for exceptional performance
    scores_exceptional = {
        'relevance': 9.5,
        'authority': 8.0,
        'engagement': 7.0,
        'clarity': 8.0,
        'impact': 8.0
    }
    assert calculator.apply_modifiers(scores_exceptional) == 0.5
    
    # Test penalty for poor performance
    scores_poor = {
        'relevance': 8.0,
        'authority': 2.5,
        'engagement': 7.0,
        'clarity': 8.0,
        'impact': 8.0
    }
    assert calculator.apply_modifiers(scores_poor) == -0.5
    
    # Test no modifier for average performance
    scores_average = {
        'relevance': 7.0,
        'authority': 6.0,
        'engagement': 7.0,
        'clarity': 8.0,
        'impact': 7.0
    }
    assert calculator.apply_modifiers(scores_average) == 0.0

def test_final_score_calculation(calculator):
    """Test final score calculation with weights and modifiers."""
    scores = {
        'relevance': 9.0,
        'authority': 8.0,
        'engagement': 7.0,
        'clarity': 8.0,
        'impact': 9.0
    }
    
    # Calculate expected weighted score
    expected_base = sum(
        score * calculator.WEIGHTS[criterion]
        for criterion, score in scores.items()
    )
    
    # Test without review count
    final_score = calculator.calculate_final_score(scores)
    assert final_score == expected_base
    
    # Test with high review count (should add statistical significance bonus)
    final_score_with_reviews = calculator.calculate_final_score(scores, 500)
    assert final_score_with_reviews > final_score

def test_final_score_validation(calculator):
    """Test validation in final score calculation."""
    # Test missing criteria
    invalid_scores = {
        'relevance': 8.0,
        'authority': 7.0
        # Missing other required criteria
    }
    with pytest.raises(ValueError):
        calculator.calculate_final_score(invalid_scores)
    
    # Test score bounds
    perfect_scores = {
        'relevance': 10.0,
        'authority': 10.0,
        'engagement': 10.0,
        'clarity': 10.0,
        'impact': 10.0
    }
    assert calculator.calculate_final_score(perfect_scores) == 10.0
    
    zero_scores = {
        'relevance': 0.0,
        'authority': 0.0,
        'engagement': 0.0,
        'clarity': 0.0,
        'impact': 0.0
    }
    assert calculator.calculate_final_score(zero_scores) == 1.0  # Minimum score
