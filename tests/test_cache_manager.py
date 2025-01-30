"""
Unit tests for the CacheManager component.
"""
import pytest
import os
import json
import time
from datetime import datetime, timedelta
from utils.cache_manager import CacheManager

@pytest.mark.unit
class TestCacheManager:
    """Test suite for CacheManager functionality."""

    def test_initialization(self, temp_cache_dir):
        """Test cache manager initialization."""
        cache_mgr = CacheManager(cache_dir=temp_cache_dir)
        
        assert os.path.exists(temp_cache_dir)
        assert cache_mgr.max_size_bytes == 100 * 1024 * 1024  # 100MB default
        assert isinstance(cache_mgr.memory_cache, dict)

    def test_basic_cache_operations(self, cache_manager):
        """Test basic cache set/get operations."""
        # Test setting and getting cache
        cache_manager.set('test_key', {'data': 'test_value'})
        result = cache_manager.get('test_key')
        
        assert result is not None
        assert result['data'] == 'test_value'
        
        # Test getting non-existent key
        assert cache_manager.get('non_existent') is None
        
        # Test deleting cache
        cache_manager.delete('test_key')
        assert cache_manager.get('test_key') is None

    def test_cache_expiry(self, cache_manager):
        """Test cache expiration functionality."""
        # Set cache with short expiry
        cache_manager.set('expiring_key', {'data': 'test'}, expire_hours=0.001)  # ~3.6 seconds
        
        # Should be available immediately
        assert cache_manager.get('expiring_key') is not None
        
        # Wait for expiration
        time.sleep(4)
        
        # Should be None after expiry
        assert cache_manager.get('expiring_key') is None

    def test_cache_size_limit(self, temp_cache_dir):
        """Test cache size limiting functionality."""
        # Create cache manager with small size limit
        small_cache = CacheManager(cache_dir=temp_cache_dir, max_size_mb=1)  # 1MB limit
        
        # Add data that should exceed cache size
        large_data = {'data': 'x' * (1024 * 1024)}  # ~1MB of data
        small_cache.set('large_key1', large_data)
        small_cache.set('large_key2', large_data)
        
        # One of the items should have been removed
        assert not (
            small_cache.get('large_key1') is not None 
            and small_cache.get('large_key2') is not None
        )

    def test_cache_persistence(self, temp_cache_dir):
        """Test cache persistence to disk."""
        # Create cache and add data
        cache_mgr = CacheManager(cache_dir=temp_cache_dir)
        test_data = {'test': 'data'}
        cache_mgr.set('persist_test', test_data)
        
        # Create new cache manager instance with same directory
        new_cache_mgr = CacheManager(cache_dir=temp_cache_dir)
        
        # Should load cached data
        assert new_cache_mgr.get('persist_test') == test_data

    def test_clear_cache(self, cache_manager):
        """Test cache clearing functionality."""
        # Add multiple items
        cache_manager.set('key1', 'value1')
        cache_manager.set('key2', 'value2')
        
        # Clear cache
        cache_manager.clear_cache()
        
        # Verify all items are removed
        assert cache_manager.get('key1') is None
        assert cache_manager.get('key2') is None
        assert cache_manager.get_cache_size() == 0

    def test_cache_stats(self, cache_manager):
        """Test cache statistics functionality."""
        # Add test data
        cache_manager.set('stats_test1', {'data': 'test1'})
        cache_manager.set('stats_test2', {'data': 'test2'})
        
        stats = cache_manager.get_cache_stats()
        
        assert isinstance(stats, dict)
        assert 'current_size_bytes' in stats
        assert 'max_size_bytes' in stats
        assert 'item_count' in stats
        assert 'expired_count' in stats
        assert stats['item_count'] == 2

    def test_concurrent_access(self, cache_manager):
        """Test cache thread safety with concurrent access."""
        from concurrent.futures import ThreadPoolExecutor
        import random
        
        def cache_operation(i):
            """Perform random cache operation."""
            op = random.choice(['set', 'get', 'delete'])
            key = f'key_{i}'
            
            if op == 'set':
                cache_manager.set(key, {'data': f'value_{i}'})
            elif op == 'get':
                cache_manager.get(key)
            else:
                cache_manager.delete(key)
                
            return True

        # Run multiple operations concurrently
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(cache_operation, range(100)))
            
        assert all(results)  # No exceptions should have occurred

    def test_invalid_cache_data(self, cache_manager):
        """Test handling of invalid cache data."""
        # Test with non-serializable object
        with pytest.raises(Exception):
            cache_manager.set('invalid', lambda x: x)  # Functions aren't JSON serializable

    def test_cache_index_corruption(self, temp_cache_dir):
        """Test recovery from corrupted cache index."""
        # Create invalid cache index file
        index_file = os.path.join(temp_cache_dir, "cache_index.json")
        with open(index_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle corrupted index gracefully
        cache_mgr = CacheManager(cache_dir=temp_cache_dir)
        assert isinstance(cache_mgr.memory_cache, dict)
        assert len(cache_mgr.memory_cache) == 0

    def test_cache_size_calculation(self, cache_manager):
        """Test accurate cache size calculation."""
        test_data = {'data': 'x' * 1000}  # Known size data
        cache_manager.set('size_test', test_data)
        
        size = cache_manager.get_cache_size()
        assert size > 0
        assert isinstance(size, int)

    @pytest.mark.slow
    def test_large_cache_performance(self, temp_cache_dir):
        """Test cache performance with large number of items."""
        cache_mgr = CacheManager(cache_dir=temp_cache_dir)
        
        # Add many items
        start_time = time.time()
        for i in range(1000):
            cache_mgr.set(f'perf_key_{i}', {'data': f'value_{i}'})
        
        # Verify reasonable performance
        total_time = time.time() - start_time
        assert total_time < 5.0  # Should complete within 5 seconds
