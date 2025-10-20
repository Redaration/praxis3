#!/usr/bin/env python3
"""
Input validation and sanitization utilities.
"""

import re
import os
from typing import Any, List, Optional, Union
from urllib.parse import urlparse

from exceptions import ValidationError, ConfigurationError
from utils import logger

class InputValidator:
    """Comprehensive input validation and sanitization."""
    
    @staticmethod
    def validate_api_key(key: str, service: str) -> str:
        """Validate API key format."""
        if not key:
            raise ValidationError(f"{service} API key is required")
        
        key = key.strip()
        
        # Basic format validation
        if service.lower() == "openrouter":
            if not key.startswith("sk-or-"):
                raise ValidationError("Invalid OpenRouter API key format")
        elif service.lower() == "runware":
            if len(key) < 20 or not re.match(r'^[A-Z0-9-]+$', key):
                raise ValidationError("Invalid Runware API key format")
        
        return key
    
    @staticmethod
    def validate_prompt(prompt: str, max_length: int = 4000) -> str:
        """Validate and sanitize prompt."""
        if not prompt:
            raise ValidationError("Prompt cannot be empty")
        
        prompt = prompt.strip()
        
        if len(prompt) > max_length:
            raise ValidationError(f"Prompt exceeds maximum length of {max_length} characters")
        
        # Remove potential injection attempts
        prompt = re.sub(r'<script.*?</script>', '', prompt, flags=re.IGNORECASE | re.DOTALL)
        prompt = re.sub(r'javascript:', '', prompt, flags=re.IGNORECASE)
        
        # Normalize whitespace
        prompt = re.sub(r'\s+', ' ', prompt)
        
        return prompt
    
    @staticmethod
    def validate_image_dimensions(width: int, height: int) -> tuple:
        """Validate image dimensions."""
        if not isinstance(width, int) or not isinstance(height, int):
            raise ValidationError("Width and height must be integers")
        
        if width <= 0 or height <= 0:
            raise ValidationError("Width and height must be positive")
        
        if width > 2048 or height > 2048:
            raise ValidationError("Maximum dimensions are 2048x2048")
        
        if width < 64 or height < 64:
            raise ValidationError("Minimum dimensions are 64x64")
        
        return width, height
    
    @staticmethod
    def validate_file_path(path: str, must_exist: bool = False) -> str:
        """Validate file path for security."""
        if not path:
            raise ValidationError("File path cannot be empty")
        
        # Normalize path
        path = os.path.normpath(path)
        
        # Check for directory traversal
        if '..' in path or path.startswith('/'):
            raise ValidationError("Invalid file path")
        
        # Check for dangerous characters
        if any(char in path for char in ['<', '>', ':', '*', '?', '|']):
            raise ValidationError("File path contains invalid characters")
        
        if must_exist and not os.path.exists(path):
            raise ValidationError(f"File does not exist: {path}")
        
        return path
    
    @staticmethod
    def validate_url(url: str) -> str:
        """Validate URL format."""
        if not url:
            raise ValidationError("URL cannot be empty")
        
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValidationError("Invalid URL format")
            
            # Allow only http/https
            if result.scheme not in ['http', 'https']:
                raise ValidationError("Only HTTP and HTTPS URLs are allowed")
            
            return url
        except Exception as e:
            raise ValidationError(f"Invalid URL: {str(e)}")
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for security."""
        if not filename:
            raise ValidationError("Filename cannot be empty")
        
        # Remove path separators
        filename = filename.replace('/', '_').replace('\\', '_')
        
        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:\"|?*]', '_', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250-len(ext)] + ext
        
        return filename
    
    @staticmethod
    def validate_positive_integer(value: Any, name: str = "value") -> int:
        """Validate positive integer."""
        try:
            value = int(value)
            if value <= 0:
                raise ValueError
            return value
        except (ValueError, TypeError):
            raise ValidationError(f"{name} must be a positive integer")
    
    @staticmethod
    def validate_batch_size(size: int, max_size: int = 100) -> int:
        """Validate batch size."""
        size = InputValidator.validate_positive_integer(size, "batch_size")
        
        if size > max_size:
            raise ValidationError(f"Batch size cannot exceed {max_size}")
        
        return size
    
    @staticmethod
    def validate_temperature(temp: float) -> float:
        """Validate temperature value."""
        try:
            temp = float(temp)
            if not 0 <= temp <= 2:
                raise ValueError
            return temp
        except (ValueError, TypeError):
            raise ValidationError("Temperature must be between 0 and 2")
    
    @staticmethod
    def validate_max_tokens(tokens: int) -> int:
        """Validate max tokens."""
        tokens = InputValidator.validate_positive_integer(tokens, "max_tokens")
        
        if tokens > 260000:  # Config.MAX_TOKENS
            raise ValidationError("Max tokens cannot exceed 260,000")
        
        return tokens
    
    @staticmethod
    def validate_model_name(model: str) -> str:
        """Validate model name."""
        if not model:
            raise ValidationError("Model name cannot be empty")
        
        model = model.strip()
        
        # Basic format validation
        if not re.match(r'^[a-zA-Z0-9\-/]+$', model):
            raise ValidationError("Invalid model name format")
        
        return model
    
    @staticmethod
    def validate_color_rgb(r: int, g: int, b: int) -> tuple:
        """Validate RGB color values."""
        for name, value in [('red', r), ('green', g), ('blue', b)]:
            if not isinstance(value, int) or not 0 <= value <= 255:
                raise ValidationError(f"{name} must be an integer between 0 and 255")
        
        return r, g, b
    
    @staticmethod
    def validate_cache_ttl(ttl: int) -> int:
        """Validate cache TTL."""
        ttl = InputValidator.validate_positive_integer(ttl, "cache_ttl")
        
        if ttl > 86400:  # 24 hours
            raise ValidationError("Cache TTL cannot exceed 24 hours")
        
        return ttl
    
    @staticmethod
    def validate_directory_path(path: str, create: bool = False) -> str:
        """Validate directory path."""
        if not path:
            raise ValidationError("Directory path cannot be empty")
        
        path = os.path.normpath(path)
        
        # Check for directory traversal
        if '..' in path:
            raise ValidationError("Invalid directory path")
        
        # Check if directory exists or can be created
        if create:
            try:
                os.makedirs(path, exist_ok=True)
            except OSError as e:
                raise ValidationError(f"Cannot create directory: {str(e)}")
        elif not os.path.isdir(path):
            raise ValidationError(f"Directory does not exist: {path}")
        
        return path

# Global validator instance
validator = InputValidator()

# Convenience functions
def validate_prompt(prompt: str) -> str:
    """Validate prompt."""
    return validator.validate_prompt(prompt)

def validate_api_key(key: str, service: str) -> str:
    """Validate API key."""
    return validator.validate_api_key(key, service)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename."""
    return validator.sanitize_filename(filename)