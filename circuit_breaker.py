#!/usr/bin/env python3
"""
Circuit breaker pattern implementation for resilient API calls.
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional
from functools import wraps

from config import config
from exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker implementation for fault tolerance."""
    
    def __init__(
        self,
        failure_threshold: int = None,
        recovery_timeout: int = None,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Time to wait before attempting recovery
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold or config.CIRCUIT_BREAKER_THRESHOLD
        self.recovery_timeout = recovery_timeout or config.HEALTH_CHECK_INTERVAL
        self.expected_exception = expected_exception
        
        self._failure_count = 0
        self._last_failure_time = None
        self._state = CircuitState.CLOSED
        
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        if self._state == CircuitState.OPEN:
            if self._last_failure_time and time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
        return self._state
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            raise ServiceUnavailableError(
                f"Circuit breaker is OPEN. Service unavailable for {self.recovery_timeout}s"
            )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _on_success(self) -> None:
        """Handle successful call."""
        self._failure_count = 0
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            logger.info("Circuit breaker CLOSED after successful call")
    
    def _on_failure(self) -> None:
        """Handle failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker OPENED after {self._failure_count} failures"
            )

def circuit_breaker(
    failure_threshold: int = None,
    recovery_timeout: int = None,
    expected_exception: type = Exception
):
    """Decorator for circuit breaker functionality."""
    def decorator(func: Callable) -> Callable:
        breaker = CircuitBreaker(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
            expected_exception=expected_exception
        )
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        
        wrapper.circuit_breaker = breaker
        return wrapper
    
    return decorator

class HealthChecker:
    """Health check system for monitoring service status."""
    
    def __init__(self):
        self.checks = {}
    
    def register_check(self, name: str, check_func: Callable[[], bool]) -> None:
        """Register a health check."""
        self.checks[name] = check_func
    
    def check_health(self) -> dict:
        """Run all health checks."""
        results = {
            "status": "healthy",
            "checks": {},
            "timestamp": time.time()
        }
        
        all_healthy = True
        for name, check_func in self.checks.items():
            try:
                is_healthy = check_func()
                results["checks"][name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "healthy": is_healthy
                }
                if not is_healthy:
                    all_healthy = False
            except Exception as e:
                results["checks"][name] = {
                    "status": "error",
                    "healthy": False,
                    "error": str(e)
                }
                all_healthy = False
        
        results["status"] = "healthy" if all_healthy else "unhealthy"
        return results

# Global health checker instance
health_checker = HealthChecker()