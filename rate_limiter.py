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
    """
    Sliding window rate limiter implementation for API request throttling.

    Uses a sliding window algorithm with deque to track request timestamps.
    Automatically removes expired requests from the window as time progresses.

    This prevents API quota exhaustion and ensures compliance with rate limits
    by tracking requests per key (e.g., per user, per API endpoint).

    Example:
        # Create a rate limiter: max 100 requests per 60 seconds
        limiter = RateLimiter(max_requests=100, window_seconds=60)

        # Check if request is allowed
        if limiter.is_allowed("user_123"):
            make_api_call()
        else:
            wait_time = limiter.get_wait_time("user_123")
            print(f"Rate limited. Wait {wait_time}s")
    """

    def __init__(
        self,
        max_requests: int = None,
        window_seconds: int = None,
        key_func: callable = None
    ):
        """
        Initialize the rate limiter with configurable limits.

        Args:
            max_requests: Maximum number of requests allowed in the time window.
                        Defaults to config.RATE_LIMIT_REQUESTS (typically 100)
            window_seconds: Size of the sliding time window in seconds.
                          Defaults to config.RATE_LIMIT_WINDOW (typically 60s)
            key_func: Optional function to generate rate limit keys dynamically.
                     Defaults to lambda returning "default" (single global limit)

        The rate limiter tracks requests per key. Use different keys to have
        separate rate limits for different users, endpoints, or operations.
        """
        self.max_requests = max_requests or config.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or config.RATE_LIMIT_WINDOW
        self.key_func = key_func or (lambda: "default")

        # Track request timestamps per key using deques for efficient operations
        self._requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, key: Optional[str] = None) -> bool:
        """
        Check if a request is allowed under the current rate limit.

        This method:
        1. Removes expired requests from the sliding window
        2. Checks if request count is under the limit
        3. If allowed, records the current request timestamp

        Args:
            key: Rate limit key (uses key_func if None)

        Returns:
            True if request is allowed, False if rate limit exceeded

        Example:
            if limiter.is_allowed("api_endpoint"):
                # Make API call
                response = api.call()
            else:
                # Handle rate limit
                log.warning("Rate limit exceeded")
        """
        key = key or self.key_func()
        now = time.time()

        # Clean expired requests outside the sliding window
        requests = self._requests[key]
        while requests and requests[0] <= now - self.window_seconds:
            requests.popleft()

        # Check if we're under the limit
        if len(requests) < self.max_requests:
            requests.append(now)  # Record this request
            return True

        return False

    def get_wait_time(self, key: Optional[str] = None) -> float:
        """
        Calculate wait time in seconds until next request is allowed.

        Args:
            key: Rate limit key (uses key_func if None)

        Returns:
            Seconds to wait (0.0 if requests are currently allowed)

        Example:
            wait = limiter.get_wait_time("user_123")
            if wait > 0:
                print(f"Please wait {wait:.1f} seconds")
        """
        key = key or self.key_func()
        requests = self._requests[key]

        # No waiting needed if under limit
        if not requests or len(requests) < self.max_requests:
            return 0.0

        # Calculate when oldest request will fall outside window
        oldest_request = requests[0]
        wait_time = self.window_seconds - (time.time() - oldest_request)
        return max(0.0, wait_time)

    def check_rate_limit(self, key: Optional[str] = None) -> None:
        """
        Check rate limit and raise exception if exceeded.

        Convenience method that combines is_allowed() check with exception raising.
        Use this for mandatory rate limit enforcement.

        Args:
            key: Rate limit key (uses key_func if None)

        Raises:
            RateLimitError: If rate limit is exceeded, includes wait time in message

        Example:
            try:
                limiter.check_rate_limit("api_calls")
                make_expensive_api_call()
            except RateLimitError as e:
                log.error(f"Rate limited: {e}")
        """
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