"""
Pytest configuration and shared fixtures.
"""
import os
import pytest
import tempfile
import shutil
from datetime import datetime

from core.rating_service import RatingService
from core.rating_calculator import RatingCalculator
from core.metrics_collector import MetricsCollector
from core.data_processor import DataProcessor
from models.resource import Resource
from utils.cache_manager import CacheManager

@pytest.fixture(scope="function")
def temp_cache_dir():
    """Provide a temporary directory for cache files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture(scope="function")
def cache_manager(temp_cache_dir):
    """Provide a CacheManager instance with temporary storage."""
    return CacheManager(cache_dir=temp_cache_dir)

@pytest.fixture(scope="function")
def rating_service(temp_cache_dir):
    """Provide a RatingService instance with temporary cache."""
    return RatingService(cache_dir=temp_cache_dir)

@pytest.fixture(scope="function")
def metrics_collector():
    """Provide a MetricsCollector instance."""
    return MetricsCollector()

@pytest.fixture(scope="function")
def data_processor():
    """Provide a DataProcessor instance."""
    return DataProcessor()

@pytest.fixture(scope="function")
def sample_resource():
    """Provide a sample Resource instance."""
    return Resource(
        title="Test Resource",
        content="""
        This is a test resource with enough content to analyze various metrics.
        It includes multiple sentences and paragraphs to ensure proper testing
        of text analysis features. The content is designed to have measurable
        engagement and clarity scores.
        """,
        author="Test Author",
        url="https://example.com/test",
        publication_date=datetime.now().isoformat(),
        metadata={
            'keywords': ['test', 'sample', 'metrics'],
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

@pytest.fixture(scope="function")
def sample_batch_resources():
    """Provide a list of sample resources for batch processing."""
    resources = []
    for i in range(3):
        resource = Resource(
            title=f"Test Resource {i+1}",
            content=f"Test content for resource {i+1}",
            author=f"Author {i+1}",
            url=f"https://example.com/test-{i+1}",
            publication_date=datetime.now().isoformat(),
            metadata={
                'keywords': ['test', f'sample-{i+1}'],
                'category': 'testing',
                'language': 'en',
                'view_count': 1000 + (i * 100),
                'avg_interaction_time': 300 + (i * 30),
                'social_shares': 150 + (i * 15),
                'total_interactions': 500 + (i * 50),
                'citations': 25 + i,
                'author_credentials_score': 8.0,
                'domain_authority': 70,
                'positive_outcomes': 7 + i,
                'conversion_rate': 0.12 + (i * 0.01),
                'user_satisfaction': 8.5,
                'review_count': 250 + (i * 25)
            }
        )
        resources.append(resource)
    return resources

@pytest.fixture(scope="session")
def test_data_dir(tmp_path_factory):
    """Create and provide a temporary directory for test data files."""
    test_dir = tmp_path_factory.mktemp("test_data")
    return test_dir

@pytest.fixture(scope="function")
def test_file(test_data_dir):
    """Create and provide a temporary test file."""
    file_path = test_data_dir / "test_file.txt"
    with open(file_path, 'w') as f:
        f.write("Test content for file operations")
    return file_path

@pytest.fixture(scope="function")
def mock_nltk_data(monkeypatch):
    """Mock NLTK data to avoid downloads during tests."""
    def mock_find(*args, **kwargs):
        return True
        
    def mock_download(*args, **kwargs):
        return True
        
    import nltk
    monkeypatch.setattr(nltk.data, "find", mock_find)
    monkeypatch.setattr(nltk, "download", mock_download)

def pytest_configure(config):
    """Add custom markers to pytest configuration."""
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")

def pytest_collection_modifyitems(config, items):
    """Add markers to test items based on location and naming."""
    for item in items:
        # Mark all tests in integration directory as integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)
            
        # Mark tests with "slow" in the name as slow tests
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)
