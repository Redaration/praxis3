#!/usr/bin/env python3
"""
Simplified demo of the enhanced AI Course Generator
Works with standard Python libraries only
"""

import os
import time
import json
from pathlib import Path

# Import core components that work with standard libraries
from config import config
from exceptions import CourseGeneratorException, ValidationError
from validation import InputValidator
from circuit_breaker import CircuitBreaker
from rate_limiter import RateLimiter

class SimpleDemo:
    """Simplified demo showing the enhanced features."""
    
    def __init__(self):
        """Initialize the demo."""
        print("🎓 AI Course Generator - Enhanced Demo")
        print("=" * 50)
        
    def demo_security(self):
        """Demonstrate security features."""
        print("\n🔒 Security Features Demo")
        print("-" * 30)
        
        # API Key validation
        try:
            print("1. API Key Validation:")
            test_key = "sk-or-v1-test-key-12345"
            validated = InputValidator.validate_api_key(test_key, "openrouter")
            print(f"   ✅ Validated: {validated}")
        except ValidationError as e:
            print(f"   ❌ Validation failed: {e}")
        
        # Input sanitization
        print("\n2. Input Sanitization:")
        malicious_input = "<script>alert('xss')</script>Hello World"
        try:
            sanitized = InputValidator.validate_prompt(malicious_input)
            print(f"   ✅ Sanitized: {sanitized}")
        except ValidationError as e:
            print(f"   ❌ Sanitization failed: {e}")
    
    def demo_circuit_breaker(self):
        """Demonstrate circuit breaker."""
        print("\n⚡ Circuit Breaker Demo")
        print("-" * 30)
        
        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=2
        )
        
        print("1. Normal operation:")
        for i in range(3):
            try:
                result = breaker.call(lambda: f"Success {i+1}")
                print(f"   ✅ {result}")
            except Exception as e:
                print(f"   ❌ {e}")
        
        print("\n2. Simulating failures:")
        for i in range(3):
            try:
                breaker.call(lambda: 1/0)
            except ZeroDivisionError:
                print(f"   ⚠️  Failure {i+1}")
            except Exception as e:
                print(f"   🔴 Circuit open: {e}")
        
        print("\n3. Recovery after timeout:")
        time.sleep(2.1)
        try:
            result = breaker.call(lambda: "Recovered!")
            print(f"   ✅ {result}")
        except Exception as e:
            print(f"   ❌ Recovery failed: {e}")
    
    def demo_rate_limiting(self):
        """Demonstrate rate limiting."""
        print("\n🔄 Rate Limiting Demo")
        print("-" * 30)
        
        limiter = RateLimiter(max_requests=3, window_seconds=5)
        
        print("1. Testing rate limits:")
        for i in range(5):
            allowed = limiter.is_allowed()
            status = "✅ Allowed" if allowed else "❌ Blocked"
            print(f"   Request {i+1}: {status}")
            time.sleep(0.5)
        
        print("\n2. Waiting for reset...")
        time.sleep(5.1)
        allowed = limiter.is_allowed()
        print(f"   After reset: {'✅ Allowed' if allowed else '❌ Blocked'}")
    
    def demo_validation(self):
        """Demonstrate input validation."""
        print("\n🧪 Input Validation Demo")
        print("-" * 30)
        
        test_cases = [
            ("Valid prompt", "Create a course about Python"),
            ("Empty prompt", ""),
            ("Long prompt", "x" * 5000),
            ("Malicious prompt", "<script>alert('hack')</script>Hello"),
        ]
        
        for name, prompt in test_cases:
            try:
                validated = InputValidator.validate_prompt(prompt)
                print(f"   ✅ {name}: {validated[:50]}...")
            except ValidationError as e:
                print(f"   ❌ {name}: {e}")
    
    def demo_configuration(self):
        """Demonstrate configuration management."""
        print("\n⚙️ Configuration Demo")
        print("-" * 30)
        
        # Show configuration values
        print("1. Configuration values:")
        print(f"   Cache enabled: {config.CACHE_ENABLED}")
        print(f"   Cache TTL: {config.CACHE_TTL}s")
        print(f"   Rate limit: {config.RATE_LIMIT_REQUESTS}/hour")
        print(f"   Health check interval: {config.HEALTH_CHECK_INTERVAL}s")
        
        # Test environment variable loading
        print("\n2. Environment variables:")
        print(f"   OPENROUTER_API_KEY: {'Set' if config.OPENROUTER_API_KEY else 'Not set'}")
        print(f"   RUNWARE_API_KEY: {'Set' if config.RUNWARE_API_KEY else 'Not set'}")
    
    def run_demo(self):
        """Run the complete demo."""
        print("🚀 Starting Enhanced AI Course Generator Demo")
        print("=" * 50)
        
        # Create demo environment
        demo_dir = Path("demo_output")
        demo_dir.mkdir(exist_ok=True)
        
        # Run all demos
        self.demo_configuration()
        self.demo_security()
        self.demo_validation()
        self.demo_rate_limiting()
        self.demo_circuit_breaker()
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("📁 Check demo_output/ for generated files")
        print("🔧 Set up your .env file with real API keys to test live functionality")

def main():
    """Main demo function."""
    demo = SimpleDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()