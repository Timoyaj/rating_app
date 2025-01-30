"""
Unit tests for the Resource model.
"""
import pytest
from datetime import datetime
from models.resource import Resource

@pytest.fixture
def sample_resource_data():
    """Fixture providing sample resource data for tests."""
    return {
        'title': 'Test Resource',
        'content': 'Test content for the resource.',
        'author': 'Test Author',
        'url': 'https://example.com/test',
        'publication_date': '2024-01-30T00:00:00Z',
        'metadata': {
            'keywords': ['test', 'sample'],
            'category': 'testing',
            'language': 'en'
        }
    }

def test_resource_initialization(sample_resource_data):
    """Test resource initialization with valid data."""
    resource = Resource(**sample_resource_data)
    
    assert resource.title == sample_resource_data['title']
    assert resource.content == sample_resource_data['content']
    assert resource.author == sample_resource_data['author']
    assert resource.url == sample_resource_data['url']
    assert resource.publication_date == sample_resource_data['publication_date']
    assert resource.metadata == sample_resource_data['metadata']
    assert resource.resource_id is not None
    assert len(resource.resource_id) == 16

def test_resource_to_dict(sample_resource_data):
    """Test conversion of resource to dictionary."""
    resource = Resource(**sample_resource_data)
    resource_dict = resource.to_dict()
    
    assert resource_dict['title'] == sample_resource_data['title']
    assert resource_dict['content'] == sample_resource_data['content']
    assert resource_dict['author'] == sample_resource_data['author']
    assert resource_dict['metadata'] == sample_resource_data['metadata']
    assert 'resource_id' in resource_dict
    assert 'scores' in resource_dict
    assert 'final_score' in resource_dict

def test_resource_from_dict(sample_resource_data):
    """Test creation of resource from dictionary."""
    original = Resource(**sample_resource_data)
    data = original.to_dict()
    recreated = Resource.from_dict(data)
    
    assert recreated.title == original.title
    assert recreated.content == original.content
    assert recreated.author == original.author
    assert recreated.url == original.url
    assert recreated.publication_date == original.publication_date
    assert recreated.metadata == original.metadata
    assert recreated.resource_id == original.resource_id

def test_update_score():
    """Test updating individual criterion scores."""
    resource = Resource(
        title="Test",
        content="Content",
        author="Author",
        url="https://example.com",
        publication_date="2024-01-30T00:00:00Z",
        metadata={'keywords': [], 'category': 'test', 'language': 'en'}
    )
    
    resource.update_score('relevance', 8.5)
    assert resource.scores['relevance'] == 8.5
    assert resource.last_rated is not None

def test_set_final_score():
    """Test setting final score with metadata."""
    resource = Resource(
        title="Test",
        content="Content",
        author="Author",
        url="https://example.com",
        publication_date="2024-01-30T00:00:00Z",
        metadata={'keywords': [], 'category': 'test', 'language': 'en'}
    )
    
    metadata = {'calculation_time': '1.2s', 'confidence': 0.95}
    resource.set_final_score(9.2, metadata)
    
    assert resource.final_score == 9.2
    assert resource.last_rated is not None
    assert resource.rating_metadata['calculation_time'] == '1.2s'
    assert resource.rating_metadata['confidence'] == 0.95

def test_score_bounds():
    """Test that scores are properly bounded between 0 and 10."""
    resource = Resource(
        title="Test",
        content="Content",
        author="Author",
        url="https://example.com",
        publication_date="2024-01-30T00:00:00Z",
        metadata={'keywords': [], 'category': 'test', 'language': 'en'}
    )
    
    # Test lower bound
    resource.update_score('test_criterion', -5.0)
    assert resource.scores['test_criterion'] == 0.0
    
    # Test upper bound
    resource.update_score('test_criterion', 15.0)
    assert resource.scores['test_criterion'] == 10.0
    
    # Test within bounds
    resource.update_score('test_criterion', 7.5)
    assert resource.scores['test_criterion'] == 7.5

def test_is_stale():
    """Test stale check functionality."""
    resource = Resource(
        title="Test",
        content="Content",
        author="Author",
        url="https://example.com",
        publication_date="2024-01-30T00:00:00Z",
        metadata={'keywords': [], 'category': 'test', 'language': 'en'}
    )
    
    # Should be stale when no rating
    assert resource.is_stale()
    
    # Should not be stale immediately after rating
    resource.update_score('test', 5.0)
    assert not resource.is_stale()
    
    # Should be stale after specified time
    resource.last_rated = datetime.now().replace(hour=0, minute=0)  # Set to start of day
    assert resource.is_stale(max_age_hours=12)
