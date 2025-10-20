#!/usr/bin/env python3
"""
Shared utilities for the AI-powered course content generation system.

This module provides common utility functions used across the application
to eliminate code duplication and improve maintainability.
"""

import os
import json
import hashlib
import logging
import time
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from functools import wraps
import asyncio
import aiofiles

from config import config
from exceptions import (
    FileOperationError, ValidationError, CacheError, 
    ConfigurationError, ResourceNotFoundError
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    def ensure_directory(path: str) -> str:
        """Ensure a directory exists, create if it doesn't."""
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
            return path
        except Exception as e:
            raise FileOperationError(f"Failed to create directory {path}: {e}")
    
    @staticmethod
    def safe_filename(filename: str, max_length: int = 255) -> str:
        """Create a safe filename by removing/replacing invalid characters."""
        import re
        # Remove or replace invalid characters
        safe = re.sub(r'[<>:"/\\|?*]', '_', filename)
        safe = re.sub(r'[^\w\-_\. ]', '_', safe)
        
        # Truncate if too long
        if len(safe) > max_length:
            name, ext = os.path.splitext(safe)
            max_name_length = max_length - len(ext)
            safe = name[:max_name_length] + ext
        
        return safe
    
    @staticmethod
    def get_file_hash(filepath: str) -> str:
        """Get MD5 hash of a file."""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            raise FileOperationError(f"Failed to hash file {filepath}: {e}")
    
    @staticmethod
    def read_json_file(filepath: str) -> Dict[str, Any]:
        """Safely read a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ResourceNotFoundError(f"File not found: {filepath}")
        except json.JSONDecodeError as e:
            raise FileOperationError(f"Invalid JSON in {filepath}: {e}")
        except Exception as e:
            raise FileOperationError(f"Failed to read {filepath}: {e}")
    
    @staticmethod
    def write_json_file(filepath: str, data: Dict[str, Any], indent: int = 2) -> None:
        """Safely write a JSON file."""
        try:
            FileUtils.ensure_directory(os.path.dirname(filepath))
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
        except Exception as e:
            raise FileOperationError(f"Failed to write {filepath}: {e}")
    
    @staticmethod
    def copy_file(src: str, dst: str) -> None:
        """Copy a file from source to destination."""
        try:
            FileUtils.ensure_directory(os.path.dirname(dst))
            shutil.copy2(src, dst)
        except Exception as e:
            raise FileOperationError(f"Failed to copy {src} to {dst}: {e}")
    
    @staticmethod
    def delete_file(filepath: str) -> None:
        """Delete a file if it exists."""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            raise FileOperationError(f"Failed to delete {filepath}: {e}")
    
    @staticmethod
    def list_files(directory: str, pattern: str = "*") -> List[str]:
        """List files in a directory matching a pattern."""
        try:
            from glob import glob
            return glob(os.path.join(directory, pattern))
        except Exception as e:
            raise FileOperationError(f"Failed to list files in {directory}: {e}")

class CacheUtils:
    """Utility class for caching operations."""
    
    @staticmethod
    def get_cache_key(*args, **kwargs) -> str:
        """Generate a cache key from arguments."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    @staticmethod
    def load_cache(key: str) -> Optional[Dict[str, Any]]:
        """Load cached data if it exists and is not expired."""
        if not config.CACHE_ENABLED:
            return None
        
        cache_path = config.get_cache_path(key)
        try:
            if os.path.exists(cache_path):
                # Check if cache is expired
                if time.time() - os.path.getmtime(cache_path) > config.CACHE_TTL:
                    os.remove(cache_path)
                    return None
                
                return FileUtils.read_json_file(cache_path)
        except Exception as e:
            logger.warning(f"Cache load failed for key {key}: {e}")
        
        return None
    
    @staticmethod
    def save_cache(key: str, data: Dict[str, Any]) -> None:
        """Save data to cache."""
        if not config.CACHE_ENABLED:
            return
        
        try:
            cache_path = config.get_cache_path(key)
            FileUtils.write_json_file(cache_path, data)
        except Exception as e:
            logger.warning(f"Cache save failed for key {key}: {e}")
    
    @staticmethod
    def clear_cache() -> None:
        """Clear all cached data."""
        try:
            cache_dir = os.path.join(config.get_current_directory() or ".", config.CACHE_DIR)
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                FileUtils.ensure_directory(cache_dir)
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")

class ValidationUtils:
    """Utility class for validation operations."""
    
    @staticmethod
    def validate_string(value: Any, min_length: int = 1, max_length: int = None, 
                       allow_empty: bool = False) -> str:
        """Validate and return a string value."""
        if not isinstance(value, str):
            raise ValidationError("Value must be a string")
        
        if not allow_empty and not value.strip():
            raise ValidationError("String cannot be empty")
        
        if len(value) < min_length:
            raise ValidationError(f"String must be at least {min_length} characters")
        
        if max_length and len(value) > max_length:
            raise ValidationError(f"String must be at most {max_length} characters")
        
        return value.strip()
    
    @staticmethod
    def validate_file_path(filepath: str, must_exist: bool = False) -> str:
        """Validate a file path."""
        if not filepath:
            raise ValidationError("File path cannot be empty")
        
        filepath = os.path.abspath(filepath)
        
        if must_exist and not os.path.exists(filepath):
            raise ResourceNotFoundError(f"File not found: {filepath}")
        
        return filepath
    
    @staticmethod
    def validate_directory_path(directory: str, create_if_missing: bool = False) -> str:
        """Validate a directory path."""
        if not directory:
            raise ValidationError("Directory path cannot be empty")
        
        directory = os.path.abspath(directory)
        
        if create_if_missing:
            FileUtils.ensure_directory(directory)
        elif not os.path.isdir(directory):
            raise ValidationError(f"Directory does not exist: {directory}")
        
        return directory
    
    @staticmethod
    def validate_positive_integer(value: Any, allow_zero: bool = False) -> int:
        """Validate and return a positive integer."""
        try:
            value = int(value)
            if value < 0 or (not allow_zero and value == 0):
                raise ValueError
            return value
        except ValueError:
            raise ValidationError("Value must be a positive integer")

class AsyncUtils:
    """Utility class for async operations."""
    
    @staticmethod
    async def read_file_async(filepath: str) -> str:
        """Asynchronously read a text file."""
        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                return await f.read()
        except Exception as e:
            raise FileOperationError(f"Failed to read {filepath}: {e}")
    
    @staticmethod
    async def write_file_async(filepath: str, content: str) -> None:
        """Asynchronously write a text file."""
        try:
            FileUtils.ensure_directory(os.path.dirname(filepath))
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(content)
        except Exception as e:
            raise FileOperationError(f"Failed to write {filepath}: {e}")

class PerformanceUtils:
    """Utility class for performance monitoring."""
    
    @staticmethod
    def timer(func):
        """Decorator to measure function execution time."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
            return result
        return wrapper
    
    @staticmethod
    def async_timer(func):
        """Decorator to measure async function execution time."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds")
            return result
        return wrapper
    
    @staticmethod
    def memory_usage():
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0
    
    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """Format bytes into human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"

class TextUtils:
    """Utility class for text processing."""
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate text to a maximum length."""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing extra whitespace and special characters."""
        import re
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,!?;:()\[\]{}"\']', '', text)
        return text.strip()
    
    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from text that might contain markdown or other formatting."""
        import re
        import json
        
        # Try to find JSON in markdown code blocks
        json_pattern = r'```(?:json)?\s*({.*?})\s*```'
        match = re.search(json_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON in the text
        try:
            # Look for JSON objects
            json_pattern = r'\{[^{}]*\}'
            matches = re.findall(json_pattern, text)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def word_count(text: str) -> int:
        """Count words in text."""
        return len(text.split())

class RetryUtils:
    """Utility class for retry operations."""
    
    @staticmethod
    def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
        """Decorator for retrying functions."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                current_delay = delay
                
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            logger.error(f"All {max_attempts} attempts failed. Last error: {e}")
                
                raise last_exception
            
            return wrapper
        return decorator
    
    @staticmethod
    def async_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
        """Decorator for retrying async functions."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                last_exception = None
                current_delay = delay
                
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {current_delay}s...")
                            await asyncio.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            logger.error(f"All {max_attempts} attempts failed. Last error: {e}")
                
                raise last_exception
            
            return wrapper
        return decorator

# Export commonly used utilities
__all__ = [
    'FileUtils', 'CacheUtils', 'ValidationUtils', 
    'AsyncUtils', 'PerformanceUtils', 'TextUtils', 'RetryUtils',
    'logger'
]