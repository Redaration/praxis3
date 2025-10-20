#!/usr/bin/env python3
"""
Enhanced test suite with comprehensive testing for all improvements.
"""

import os
import sys
import json
import tempfile
import shutil
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Import our new components
from config import config
from exceptions import CourseGeneratorException, LLMError, ImageGenerationError
from validation import InputValidator, validate_prompt, validate_api_key
from circuit_breaker import CircuitBreaker, health_checker
from rate_limiter import RateLimiter, llm_rate_limiter, image_rate_limiter
from metrics import metrics_collector, get_metrics
from health_check import health_manager, check_health
from utils import logger

class TestSecurity(unittest.TestCase):
    """Test security improvements."""
    
    def test_api_key_validation(self):
        """Test API key validation."""
        # Test valid OpenRouter key
        valid_key = "sk-or-v1-abc123def456"
        self.assertEqual(validate_api_key(valid_key, "openrouter"), valid_key)
        
        # Test invalid OpenRouter key
        with self.assertRaises(ValidationError):
            validate_api_key("invalid-key", "openrouter")
        
        # Test empty key
        with self.assertRaises(ValidationError):
            validate_api_key("", "openrouter")
    
    def test_prompt_sanitization(self):
        """Test prompt sanitization."""
        # Test XSS prevention
        malicious_prompt = "<script>alert('xss')</script>Hello World"
        sanitized = validate_prompt(malicious_prompt)
        self.assertNotIn("<script>", sanitized)
        
        # Test length validation
        long_prompt = "x" * 5000
        with self.assertRaises(ValidationError):
            validate_prompt(long_prompt)
    
    def test_file_path_validation(self):
        """Test file path validation."""
        # Test directory traversal prevention
        with self.assertRaises(ValidationError):
            InputValidator.validate_file_path("../../../etc/passwd")
        
        # Test valid path
        valid_path = "safe_directory/file.txt"
        self.assertEqual(InputValidator.validate_file_path(valid_path), valid_path)

class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker functionality."""
    
    def test_circuit_breaker_states(self):
        """Test circuit breaker state transitions."""
        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=1
        )
        
        # Initial state should be CLOSED
        self.assertEqual(breaker.state.value, "closed")
        
        # Simulate failures
        for _ in range(3):
            try:
                breaker.call(lambda: 1/0)
            except ZeroDivisionError:
                pass
        
        # Should be OPEN after failures
        self.assertEqual(breaker.state.value, "open")
        
        # Should allow call after timeout
        time.sleep(1.1)
        self.assertEqual(breaker.state.value, "half_open")

class TestRateLimiter(unittest.TestCase):
    """Test rate limiting functionality."""
    
    def test_rate_limiting(self):
        """Test rate limiting behavior."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)
        
        # First two requests should be allowed
        self.assertTrue(limiter.is_allowed())
        self.assertTrue(limiter.is_allowed())
        
        # Third request should be blocked
        self.assertFalse(limiter.is_allowed())
        
        # Wait and try again
        time.sleep(1.1)
        self.assertTrue(limiter.is_allowed())
    
    def test_sliding_window(self):
        """Test sliding window rate limiter."""
        limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=1)
        
        # Test basic functionality
        self.assertTrue(limiter.is_allowed())
        self.assertTrue(limiter.is_allowed())
        self.assertFalse(limiter.is_allowed())
        
        # Test remaining requests
        self.assertEqual(limiter.get_remaining_requests(), 0)

class TestMetrics(unittest.TestCase):
    """Test metrics collection."""
    
    def setUp(self):
        """Reset metrics before each test."""
        metrics_collector.reset_metrics()
    
    def test_metrics_collection(self):
        """Test basic metrics collection."""
        initial_metrics = get_metrics()
        self.assertEqual(initial_metrics['api_calls'], 0)
        
        # Record some metrics
        metrics_collector.record_api_call("test", "endpoint", 0.5)
        metrics_collector.record_cache_hit()
        metrics_collector.record_cache_miss()
        
        updated_metrics = get_metrics()
        self.assertEqual(updated_metrics['api_calls'], 1)
        self.assertEqual(updated_metrics['cache_hits'], 1)
        self.assertEqual(updated_metrics['cache_misses'], 1)
    
    def test_error_rate_calculation(self):
        """Test error rate calculation."""
        # Record 10 calls with 2 errors
        for i in range(8):
            metrics_collector.record_api_call("test", "endpoint", 0.1)
        for i in range(2):
            metrics_collector.record_api_call("test", "endpoint", 0.1, "error")
        
        metrics = get_metrics()
        self.assertAlmostEqual(metrics['error_rate'], 0.2, places=2)

class TestHealthChecks(unittest.TestCase):
    """Test health check system."""
    
    def test_health_check_registration(self):
        """Test health check registration."""
        def dummy_check():
            return True
        
        health_checker.register_check("dummy", dummy_check)
        self.assertIn("dummy", health_manager.checks)
    
    def test_health_status(self):
        """Test health status reporting."""
        status = check_health()
        self.assertIn("status", status)
        self.assertIn("checks", status)
        self.assertIn("timestamp", status)
    
    def test_detailed_health(self):
        """Test detailed health information."""
        detailed = health_manager.get_detailed_status()
        self.assertIn("status", detailed)
        self.assertIn("checks", detailed)
        self.assertIn("system", detailed)

class TestIntegration(unittest.TestCase):
    """Integration tests for all components."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create test configuration
        with open("current_directory.txt", "w") as f:
            f.write(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_full_workflow(self):
        """Test complete workflow with all components."""
        # Test configuration validation
        with patch.dict(os.environ, {
            'OPENROUTER_API_KEY': 'sk-or-v1-test-key',
            'RUNWARE_API_KEY': 'TEST-KEY-12345'
        }):
            config.validate_config()
        
        # Test validation
        prompt = validate_prompt("Generate a course about Python programming")
        self.assertIsInstance(prompt, str)
        
        # Test rate limiting
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for i in range(5):
            self.assertTrue(limiter.is_allowed())
        self.assertFalse(limiter.is_allowed())
        
        # Test health checks
        health_status = check_health()
        self.assertIsInstance(health_status, dict)
        
        # Test metrics
        metrics = get_metrics()
        self.assertIsInstance(metrics, dict)
        self.assertIn('api_calls', metrics)

class TestPerformance(unittest.TestCase):
    """Performance testing."""
    
    def test_rate_limiter_performance(self):
        """Test rate limiter performance."""
        limiter = RateLimiter(max_requests=1000, window_seconds=1)
        
        start_time = time.time()
        for i in range(1000):
            limiter.is_allowed()
        duration = time.time() - start_time
        
        # Should complete 1000 checks in reasonable time
        self.assertLess(duration, 0.1)
    
    def test_circuit_breaker_performance(self):
        """Test circuit breaker performance."""
        breaker = CircuitBreaker(failure_threshold=1000, recovery_timeout=1)
        
        start_time = time.time()
        for i in range(1000):
            breaker.call(lambda: True)
        duration = time.time() - start_time
        
        # Should complete 1000 calls in reasonable time
        self.assertLess(duration, 0.1)

class TestErrorHandling(unittest.TestCase):
    """Test error handling improvements."""
    
    def test_validation_errors(self):
        """Test validation error handling."""
        with self.assertRaises(ValidationError):
            validate_prompt("")
        
        with self.assertRaises(ValidationError):
            InputValidator.validate_file_path("../../../etc/passwd")
    
    def test_circuit_breaker_errors(self):
        """Test circuit breaker error handling."""
        breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=1)
        
        # Force open state
        try:
            breaker.call(lambda: 1/0)
        except ZeroDivisionError:
            pass
        
        # Should raise ServiceUnavailableError
        with self.assertRaises(ServiceUnavailableError):
            breaker.call(lambda: True)

def run_comprehensive_tests():
    """Run all comprehensive tests."""
    print("=" * 80)
    print("AI Course Generator - Comprehensive Test Suite")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestSecurity))
    suite.addTest(unittest.makeSuite(TestCircuitBreaker))
    suite.addTest(unittest.makeSuite(TestRateLimiter))
    suite.addTest(unittest.makeSuite(TestMetrics))
    suite.addTest(unittest.makeSuite(TestHealthChecks))
    suite.addTest(unittest.makeSuite(TestIntegration))
    suite.addTest(unittest.makeSuite(TestPerformance))
    suite.addTest(unittest.makeSuite(TestErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 80)
    print("Test Results Summary")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = result.wasSuccessful()
    print(f"\nOverall: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    return success

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)