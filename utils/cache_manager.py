"""
Cache management utility for optimizing performance.
"""
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import os
from threading import Lock

class CacheManager:
    """Manages caching of rating results and frequently accessed data."""
    
    def __init__(self, cache_dir: str = ".cache", max_size_mb: int = 100):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            max_size_mb: Maximum cache size in megabytes
        """
        self.cache_dir = cache_dir
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.memory_cache: Dict[str, Tuple[Any, datetime]] = {}
        self.cache_lock = Lock()
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        # Load existing cache from disk
        self._load_cache()

    def _load_cache(self) -> None:
        """Load cached data from disk into memory."""
        try:
            cache_file = os.path.join(self.cache_dir, "cache_index.json")
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    index = json.load(f)
                    
                for key, metadata in index.items():
                    data_file = os.path.join(self.cache_dir, f"{key}.json")
                    if os.path.exists(data_file):
                        with open(data_file, 'r') as f:
                            data = json.load(f)
                            expiry = datetime.fromisoformat(metadata['expiry'])
                            if expiry > datetime.now():
                                self.memory_cache[key] = (data, expiry)
                            else:
                                # Clean up expired cache files
                                os.remove(data_file)
        except Exception as e:
            print(f"Error loading cache: {e}")
            # If cache is corrupted, clear it
            self.clear_cache()

    def _save_cache_index(self) -> None:
        """Save cache index to disk."""
        try:
            index = {
                key: {
                    'expiry': expiry.isoformat(),
                    'size': len(json.dumps(data))
                }
                for key, (data, expiry) in self.memory_cache.items()
            }
            
            cache_file = os.path.join(self.cache_dir, "cache_index.json")
            with open(cache_file, 'w') as f:
                json.dump(index, f)
        except Exception as e:
            print(f"Error saving cache index: {e}")

    def _save_cache_item(self, key: str, data: Any) -> None:
        """
        Save individual cache item to disk.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        try:
            data_file = os.path.join(self.cache_dir, f"{key}.json")
            with open(data_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving cache item {key}: {e}")

    def _cleanup_old_cache(self) -> None:
        """Remove oldest cache entries when size limit is exceeded."""
        current_size = sum(
            len(json.dumps(data)) 
            for data, _ in self.memory_cache.values()
        )
        
        if current_size > self.max_size_bytes:
            # Sort by expiry time and remove oldest entries
            sorted_cache = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1][1]  # Sort by expiry timestamp
            )
            
            while current_size > self.max_size_bytes and sorted_cache:
                key, (data, _) = sorted_cache.pop(0)
                current_size -= len(json.dumps(data))
                del self.memory_cache[key]
                
                # Remove from disk
                try:
                    os.remove(os.path.join(self.cache_dir, f"{key}.json"))
                except OSError:
                    pass

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve item from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data if available and not expired, None otherwise
        """
        with self.cache_lock:
            if key in self.memory_cache:
                data, expiry = self.memory_cache[key]
                if expiry > datetime.now():
                    return data
                else:
                    # Remove expired item
                    del self.memory_cache[key]
                    try:
                        os.remove(os.path.join(self.cache_dir, f"{key}.json"))
                    except OSError:
                        pass
        return None

    def set(self, key: str, value: Any, expire_hours: int = 24) -> None:
        """
        Store item in cache.
        
        Args:
            key: Cache key
            value: Data to cache
            expire_hours: Hours until cache expiry
        """
        with self.cache_lock:
            expiry = datetime.now() + timedelta(hours=expire_hours)
            self.memory_cache[key] = (value, expiry)
            
            # Save to disk
            self._save_cache_item(key, value)
            self._save_cache_index()
            
            # Cleanup if needed
            self._cleanup_old_cache()

    def delete(self, key: str) -> None:
        """
        Remove item from cache.
        
        Args:
            key: Cache key to remove
        """
        with self.cache_lock:
            if key in self.memory_cache:
                del self.memory_cache[key]
                try:
                    os.remove(os.path.join(self.cache_dir, f"{key}.json"))
                except OSError:
                    pass
                self._save_cache_index()

    def clear_cache(self) -> None:
        """Clear all cached data."""
        with self.cache_lock:
            self.memory_cache.clear()
            
            # Remove all cache files
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except OSError:
                    pass

    def get_cache_size(self) -> int:
        """
        Get current cache size in bytes.
        
        Returns:
            int: Current cache size in bytes
        """
        return sum(
            len(json.dumps(data)) 
            for data, _ in self.memory_cache.values()
        )

    def get_cache_stats(self) -> Dict[str, any]:
        """
        Get cache statistics.
        
        Returns:
            Dict containing cache statistics
        """
        current_size = self.get_cache_size()
        item_count = len(self.memory_cache)
        
        expired_count = sum(
            1 for _, expiry in self.memory_cache.values()
            if expiry <= datetime.now()
        )
        
        return {
            'current_size_bytes': current_size,
            'max_size_bytes': self.max_size_bytes,
            'item_count': item_count,
            'expired_count': expired_count,
            'size_used_percentage': (current_size / self.max_size_bytes) * 100
        }
