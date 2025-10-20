#!/usr/bin/env python3
"""
Caching system for API responses and computed results.

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
from exceptions import CacheError
from utils import FileUtils, logger

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
        """Store a value in cache."""
        try:
            ttl = ttl or config.CACHE_TTL
            cache_path = self._get_cache_path(key)
            metadata_path = self._get_metadata_path(key)
            
            # Store the value
            with open(cache_path, 'wb') as f:
                pickle.dump(value, f)
            
            # Store metadata
            metadata = {
                'created': time.time(),
                'ttl': ttl,
                'expires': time.time() + ttl
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f)
                
            logger.debug(f"Cached value for key: {key}")
            
        except Exception as e:
            raise CacheError(f"Failed to cache value: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache."""
        try:
            cache_path = self._get_cache_path(key)
            metadata_path = self._get_metadata_path(key)
            
            # Check if cache exists
            if not os.path.exists(cache_path) or not os.path.exists(metadata_path):
                return None
            
            # Check if cache is expired
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            if time.time() > metadata['expires']:
                self.delete(key)
                return None
            
            # Load cached value
            with open(cache_path, 'rb') as f:
                value = pickle.load(f)
            
            logger.debug(f"Retrieved cached value for key: {key}")
            return value
            
        except Exception as e:
            logger.warning(f"Failed to retrieve cached value: {e}")
            return None
    
    def delete(self, key: str) -> None:
        """Delete a cached value."""
        try:
            cache_path = self._get_cache_path(key)
            metadata_path = self._get_metadata_path(key)
            
            if os.path.exists(cache_path):
                os.remove(cache_path)
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
                
            logger.debug(f"Deleted cached value for key: {key}")
            
        except Exception as e:
            logger.warning(f"Failed to delete cached value: {e}")
    
    def exists(self, key: str) -> bool:
        """Check if a cached value exists and is not expired."""
        return self.get(key) is not None
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """Clear cache entries matching a pattern."""
        try:
            cleared = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    key = filename[:-6]  # Remove .cache extension
                    if pattern is None or pattern in key:
                        self.delete(key)
                        cleared += 1
            
            logger.info(f"Cleared {cleared} cache entries")
            return cleared
            
        except Exception as e:
            raise CacheError(f"Failed to clear cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            total_files = 0
            total_size = 0
            expired_files = 0
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    total_files += 1
                    filepath = os.path.join(self.cache_dir, filename)
                    total_size += os.path.getsize(filepath)
                    
                    # Check if expired
                    key = filename[:-6]
                    if not self.exists(key):
                        expired_files += 1
            
            return {
                'total_entries': total_files,
                'total_size_bytes': total_size,
                'total_size_formatted': FileUtils.format_bytes(total_size),
                'expired_entries': expired_files,
                'cache_dir': self.cache_dir
            }
            
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {}
    
    def cleanup_expired(self) -> int:
        """Clean up expired cache entries."""
        try:
            cleaned = 0
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.cache'):
                    key = filename[:-6]
                    if not self.exists(key):
                        cleaned += 1
            
            logger.info(f"Cleaned up {cleaned} expired cache entries")
            return cleaned
            
        except Exception as e:
            raise CacheError(f"Failed to cleanup expired cache: {e}")

class CachedFunction:
    """Decorator for caching function results."""
    
    def __init__(self, ttl: Optional[int] = None, key_prefix: str = ""):
        self.ttl = ttl or config.CACHE_TTL
        self.key_prefix = key_prefix
        self.cache_manager = CacheManager()

    def _safe_serialize(self, value: Any) -> Any:
        """Convert values to JSON-serializable forms for cache keys."""
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, (list, tuple, set)):
            return [self._safe_serialize(v) for v in value]
        if isinstance(value, dict):
            return {
                str(k): self._safe_serialize(v)
                for k, v in value.items()
            }
        return repr(value)

    def _generate_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate a cache key for the function."""
        args_list = list(args)
        if args_list and hasattr(args_list[0], "__class__"):
            args_list = args_list[1:]

        key_data = {
            'func': func_name,
            'args': [self._safe_serialize(arg) for arg in args_list],
            'kwargs': {
                str(k): self._safe_serialize(v)
                for k, v in sorted(kwargs.items())
            } if kwargs else {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = self._generate_cache_key(func.__name__, *args, **kwargs)
            if self.key_prefix:
                key = f"{self.key_prefix}_{key}"
            
            # Try to get from cache
            cached_result = self.cache_manager.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            self.cache_manager.set(key, result, self.ttl)
            
            logger.debug(f"Cache miss for {func.__name__}, stored result")
            return result
        
        return wrapper

class AsyncCachedFunction:
    """Decorator for caching async function results."""
    
    def __init__(self, ttl: Optional[int] = None, key_prefix: str = ""):
        self.ttl = ttl or config.CACHE_TTL
        self.key_prefix = key_prefix
        self.cache_manager = CacheManager()

    def _safe_serialize(self, value: Any) -> Any:
        """Convert values to JSON-serializable forms for cache keys."""
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, (list, tuple, set)):
            return [self._safe_serialize(v) for v in value]
        if isinstance(value, dict):
            return {
                str(k): self._safe_serialize(v)
                for k, v in value.items()
            }
        return repr(value)
    
    def __call__(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = self._generate_cache_key(func.__name__, *args, **kwargs)
            if self.key_prefix:
                key = f"{self.key_prefix}_{key}"
            
            # Try to get from cache
            cached_result = self.cache_manager.get(key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            self.cache_manager.set(key, result, self.ttl)
            
            logger.debug(f"Cache miss for {func.__name__}, stored result")
            return result
        
        return wrapper
    
    def _generate_cache_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate a cache key for async functions."""
        args_list = list(args)
        if args_list and hasattr(args_list[0], "__class__"):
            args_list = args_list[1:]

        key_data = {
            'func': func_name,
            'args': [self._safe_serialize(arg) for arg in args_list],
            'kwargs': {
                str(k): self._safe_serialize(v)
                for k, v in sorted(kwargs.items())
            } if kwargs else {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

# Global cache manager instance
cache_manager = CacheManager()

# Convenience decorators
cached = CachedFunction
async_cached = AsyncCachedFunction

# Convenience functions
def cache_get(key: str) -> Optional[Any]:
    """Get value from global cache."""
    return cache_manager.get(key)

def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> None:
    """Set value in global cache."""
    cache_manager.set(key, value, ttl)

def cache_delete(key: str) -> None:
    """Delete value from global cache."""
    cache_manager.delete(key)

def cache_clear(pattern: Optional[str] = None) -> int:
    """Clear cache entries."""
    return cache_manager.clear(pattern)

def cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return cache_manager.get_stats()

# Export commonly used items
__all__ = [
    'CacheManager', 'CachedFunction', 'AsyncCachedFunction',
    'cache_manager', 'cached', 'async_cached',
    'cache_get', 'cache_set', 'cache_delete', 'cache_clear', 'cache_stats'
]
