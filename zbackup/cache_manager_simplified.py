#!/usr/bin/env python3
"""
Simplified caching system for API responses and computed results.

This module provides a comprehensive caching system to improve performance
by storing and reusing API responses and computed results.
"""

import os
import json
import time
import hashlib
import pickle
from typing import Any, Optional, Dict, List, Callable
from functools import wraps

from config import config
from utils_simplified import FileUtils, logger
from exceptions import CacheError

class CacheManager:
    """Centralized cache management system."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize the cache manager."""
        self.cache_dir = cache_dir or os.path.join(
            config.get_current_directory() or ".", 
            config.CACHE_DIR
        )
        FileUtils.ensure_directory(self.cache_dir)
        
    def _get_cache_path(self, key: str) -> str:
        """Get the full path for a cache file."""
        safe_key = FileUtils.safe_filename(key)
        return os.path.join(self.cache_dir, f"{safe_key}.cache")
    
    def _get_metadata_path(self, key: str) -> str:
        """Get the full path for cache metadata."""
        safe_key = FileUtils.safe_filename(key)
        return os.path.join(self.cache_dir, f"{safe_key}.meta")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else []
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache."""
        try:
            cache_path = self._get_cache_path(key)
            metadata_path = self._get_metadata_path(key)
            
            # Save the value
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            
            # Save metadata
            metadata = {
                'created': time.time(),
                'ttl': ttl or config.CACHE_TTL
            }
            FileUtils.write_json_file(metadata_path, metadata)
            
            logger.debug(f"Cached value for key: {key}")
            
        except Exception as e:
            logger.warning(f"Failed to cache value: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        try:
            cache_path = self._get_cache_path(key)
            metadata_path = self._get_metadata_path(key)
            
            if not os.path.exists(cache_path) or not os.path.exists(metadata_path):
                return None
            
            # Check if cache is expired
            metadata = FileUtils.read_json_file(metadata_path)
            created = metadata.get('created', 0)
            ttl = metadata.get('ttl', config.CACHE_TTL)
            
            if time.time() - created > ttl:
                # Cache expired
                self.delete(key)
                return None
            
            # Load the cached value
            with open(cache_path, 'rb') as f:
                value = pickle.load(f)
            
            logger.debug(f"Retrieved cached value for key: {key}")
            return value
            
        except Exception as e:
            logger.warning(f"Failed to retrieve cached value: {e}")
            return None
    
    def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        try:
            cache_path = self._get_cache_path(key)
            metadata_path = self._get_metadata_path(key)
            
            FileUtils.delete_file(cache_path)
            FileUtils.delete_file(metadata_path)
            
            logger.debug(f"Deleted cache for key: {key}")
            
        except Exception as e:
            logger.warning(f"Failed to delete cache: {e}")
    
    def clear(self) -> None:
        """Clear all cached data."""
        try:
            if os.path.exists(self.cache_dir):
                import shutil
                shutil.rmtree(self.cache_dir)
                FileUtils.ensure_directory(self.cache_dir)
            logger.info("Cache cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
    
    def cached(self, ttl: Optional[int] = None):
        """Decorator to cache function results."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                key = self._generate_key(*key_parts)
                
                # Try to get from cache
                cached_result = self.get(key)
                if cached_result is not None:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(key, result, ttl)
                
                return result
            
            return wrapper
        return decorator
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            files = FileUtils.list_files(self.cache_dir, "*.cache")
            total_size = 0
            for file in files:
                total_size += os.path.getsize(file)
            
            return {
                'total_files': len(files),
                'total_size': total_size,
                'cache_dir': self.cache_dir
            }
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {'total_files': 0, 'total_size': 0, 'cache_dir': self.cache_dir}

# Global cache manager instance
cache_manager = CacheManager()

# Decorator for easy caching
def cached(ttl: Optional[int] = None):
    """Decorator to cache function results using the global cache manager."""
    return cache_manager.cached(ttl)

# Export commonly used functions
__all__ = ['CacheManager', 'cache_manager', 'cached']