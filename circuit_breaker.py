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
    """
    Enumeration of possible circuit breaker states.

    States:
        CLOSED: Normal operation - requests pass through
        OPEN: Circuit is open due to failures - requests are blocked
        HALF_OPEN: Testing recovery - limited requests allowed to test service health
    """
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance and graceful degradation.

    The circuit breaker pattern prevents cascading failures by:
    1. CLOSED state: All requests pass through normally
    2. After N failures: Opens circuit, blocking all requests
    3. OPEN state: Fails fast without calling the failing service
    4. After timeout: Transitions to HALF_OPEN to test recovery
    5. HALF_OPEN state: Allows one request through to test service health
    6. If successful: Returns to CLOSED state
    7. If fails: Returns to OPEN state

    This protects systems from repeatedly calling failing services and allows
    time for recovery.

    Reference: Michael Nygard's "Release It!" pattern
    """

    def __init__(
        self,
        failure_threshold: int = None,
        recovery_timeout: int = None,
        expected_exception: type = Exception
    ):
        """
        Initialize the circuit breaker with configurable thresholds.

        Args:
            failure_threshold: Number of consecutive failures before opening circuit.
                             Defaults to config.CIRCUIT_BREAKER_THRESHOLD (typically 5)
            recovery_timeout: Seconds to wait before attempting recovery (testing service).
                            Defaults to config.HEALTH_CHECK_INTERVAL (typically 300s)
            expected_exception: Exception type to catch and count as failure.
                              Defaults to Exception (catches all)

        Example:
            # Create circuit breaker for API calls
            breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

            # Use it to wrap a potentially failing operation
            try:
                result = breaker.call(risky_api_call, arg1, arg2)
            except ServiceUnavailableError:
                # Circuit is open - use fallback
                result = use_cached_data()
        """
        self.failure_threshold = failure_threshold or config.CIRCUIT_BREAKER_THRESHOLD
        self.recovery_timeout = recovery_timeout or config.HEALTH_CHECK_INTERVAL
        self.expected_exception = expected_exception

        # Internal state tracking
        self._failure_count = 0
        self._last_failure_time = None
        self._state = CircuitState.CLOSED
        
    @property
    def state(self) -> CircuitState:
        """
        Get the current state of the circuit breaker.

        Automatically transitions from OPEN to HALF_OPEN if recovery timeout has elapsed.

        Returns:
            Current CircuitState (CLOSED, OPEN, or HALF_OPEN)
        """
        # Check if we should transition from OPEN to HALF_OPEN
        if self._state == CircuitState.OPEN:
            if self._last_failure_time and time.time() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
        return self._state

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with circuit breaker protection.

        If the circuit is OPEN, immediately raises ServiceUnavailableError without
        calling the function (fail-fast behavior). Otherwise, calls the function
        and tracks success/failure.

        Args:
            func: The function to execute
            *args: Positional arguments to pass to func
            **kwargs: Keyword arguments to pass to func

        Returns:
            The return value from func

        Raises:
            ServiceUnavailableError: If circuit is OPEN (too many recent failures)
            expected_exception: If func raises an exception (also triggers failure count)

        Example:
            result = breaker.call(api_client.fetch_data, user_id=123)
        """
        # Fail fast if circuit is open
        if self.state == CircuitState.OPEN:
            raise ServiceUnavailableError(
                f"Circuit breaker is OPEN. Service unavailable for {self.recovery_timeout}s"
            )

        try:
            # Execute the protected function
            result = func(*args, **kwargs)
            self._on_success()  # Reset failure count and potentially close circuit
            return result
        except self.expected_exception as e:
            self._on_failure()  # Increment failure count and potentially open circuit
            raise

    def _on_success(self) -> None:
        """
        Handle a successful function call.

        Resets the failure count to zero. If in HALF_OPEN state (testing recovery),
        transitions back to CLOSED state (normal operation).
        """
        self._failure_count = 0
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.CLOSED
            logger.info("Circuit breaker CLOSED after successful call")

    def _on_failure(self) -> None:
        """
        Handle a failed function call.

        Increments failure count and records failure time. If failure count
        reaches the threshold, opens the circuit to prevent further calls.
        """
        self._failure_count += 1
        self._last_failure_time = time.time()

        # Open circuit if we've hit the failure threshold
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