#!/usr/bin/env python3
"""
Rate limiting implementation for API calls.
"""

import time
import logging
from typing import Dict, Optional
from functools import wraps
from collections import defaultdict, deque

from config import config
from exceptions import RateLimitError

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(
        self,
        max_requests: int = None,
        window_seconds: int = None,
        key_func: callable = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
            key_func: Function to generate rate limit key
        """
        self.max_requests = max_requests or config.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or config.RATE_LIMIT_WINDOW
        self.key_func = key_func or (lambda: "default")
        
        self._requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, key: Optional[str] = None) -> bool:
        """Check if request is allowed."""
        key = key or self.key_func()
        now = time.time()
        
        # Clean old requests
        requests = self._requests[key]
        while requests and requests[0] <= now - self.window_seconds:
            requests.popleft()
        
        # Check if under limit
        if len(requests) < self.max_requests:
            requests.append(now)
            return True
        
        return False
    
    def get_wait_time(self, key: Optional[str] = None) -> float:
        """Get wait time until next request is allowed."""
        key = key or self.key_func()
        requests = self._requests[key]
        
        if not requests or len(requests) < self.max_requests:
            return 0.0
        
        oldest_request = requests[0]
        wait_time = self.window_seconds - (time.time() - oldest_request)
        return max(0.0, wait_time)
    
    def check_rate_limit(self, key: Optional[str] = None) -> None:
        """Check rate limit and raise exception if exceeded."""
        if not self.is_allowed(key):
            wait_time = self.get_wait_time(key)
            raise RateLimitError(
                f"Rate limit exceeded. Try again in {wait_time:.1f} seconds"
            )

class SlidingWindowRateLimiter:
    """Sliding window rate limiter with sub-second precision."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
    
    def is_allowed(self) -> bool:
        """Check if request is allowed."""
        now = time.time()
        
        # Remove old requests outside the window
        while self.requests and self.requests[0] <= now - self.window_seconds:
            self.requests.popleft()
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False
    
    def get_remaining_requests(self) -> int:
        """Get remaining requests in current window."""
        now = time.time()
        
        # Remove old requests
        while self.requests and self.requests[0] <= now - self.window_seconds:
            self.requests.popleft()
        
        return max(0, self.max_requests - len(self.requests))

# Global rate limiters
llm_rate_limiter = RateLimiter(
    max_requests=config.RATE_LIMIT_REQUESTS,
    window_seconds=config.RATE_LIMIT_WINDOW,
    key_func=lambda: "llm_api"
)

image_rate_limiter = RateLimiter(
    max_requests=config.RATE_LIMIT_REQUESTS // 2,  # Stricter for image generation
    window_seconds=config.RATE_LIMIT_WINDOW,
    key_func=lambda: "image_api"
)

def rate_limit(limiter: RateLimiter):
    """Decorator for rate limiting."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter.check_rate_limit()
            return func(*args, **kwargs)
        return wrapper
    return decorator