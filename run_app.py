#!/usr/bin/env python3
"""
Simple application runner for the AI Course Generator
Works with existing codebase and demonstrates core functionality
"""

import os
import sys
import time
from pathlib import Path

# Import core components that work with standard libraries
from config import config
from exceptions import CourseGeneratorException, ValidationError
from validation import InputValidator
from circuit_breaker import CircuitBreaker
from rate_limiter import RateLimiter
from cache_manager import cache_manager
from utils import logger

class SimpleApp:
    """Simple application runner for the AI Course Generator."""
    
    def __init__(self):
        """Initialize the application."""
        print("🎓 AI Course Generator - Simple Runner")
        print("=" * 50)
        
        # Set up environment
        self.setup_environment()
        
    def setup_environment(self):
        """Set up the application environment."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open("current_directory.txt", "w") as f:
            f.write(current_dir)
        
        print(f"📁 Working directory: {current_dir}")
        
    def display_menu(self):
        """Display the main menu."""
        print("\n" + "="*50)
        print("🎓 AI Course Generator - Menu")
        print("="*50)
        print("1. 🔍 Configuration Check")
        print("2. 🔒 Security Validation")
        print("3. ⚡ Circuit Breaker Demo")
        print("4. 🔄 Rate Limiting Demo")
        print("5. 🧪 Input Validation")
        print("6. 🧹 Cache Management")
        print("7. 📊 System Status")
        print("8. 🧪 Run Tests")
        print("0. ❌ Exit")
        print("="*50)
    
    def config_check(self):
        """Check configuration."""
        print("\n🔍 Configuration Check")
        print("-" * 30)
        
        try:
            print(f"Cache enabled: {config.CACHE_ENABLED}")
            print(f"Cache TTL: {config.CACHE_TTL}s")
            print(f"Rate limit: {config.RATE_LIMIT_REQUESTS}/hour")
            print(f"Health check interval: {config.HEALTH_CHECK_INTERVAL}s")
            
            # Check API keys
            openrouter_set = bool(config.OPENROUTER_API_KEY)
            runware_set = bool(config.RUNWARE_API_KEY)
            
            print(f"OpenRouter API key: {'✅ Set' if openrouter_set else '❌ Not set'}")
            print(f"Runware API key: {'✅ Set' if runware_set else '❌ Not set'}")
            
        except Exception as e:
            print(f"❌ Configuration error: {e}")
    
    def security_demo(self):
        """Demonstrate security features."""
        print("\n🔒 Security Features")
        print("-" * 30)
        
        # API Key validation
        print("1. API Key Validation:")
        test_keys = [
            ("sk-or-v1-valid-key-12345", "openrouter"),
            ("invalid-key", "openrouter"),
            ("TEST-KEY-12345", "runware"),
        ]
        
        for key, service in test_keys:
            try:
                validated = InputValidator.validate_api_key(key, service)
                print(f"   ✅ {service}: {key[:15]}... - Valid")
            except ValidationError as e:
                print(f"   ❌ {service}: {key[:15]}... - {e}")
    
    def circuit_breaker_demo(self):
        """Demonstrate circuit breaker."""
        print("\n⚡ Circuit Breaker Demo")
        print("-" * 30)
        
        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=2
        )
        
        print("Testing circuit breaker...")
        
        # Test successful calls
        for i in range(3):
            try:
                result = breaker.call(lambda: f"Success {i+1}")
                print(f"   ✅ {result}")
            except Exception as e:
                print(f"   ❌ {e}")
        
        # Test failures
        print("\nSimulating failures...")
        for i in range(3):
            try:
                breaker.call(lambda: 1/0)
            except ZeroDivisionError:
                print(f"   ⚠️  Failure {i+1}")
            except Exception as e:
                print(f"   🔴 Circuit open: {e}")
        
        # Test recovery
        print("\nTesting recovery...")
        time.sleep(2.1)
        try:
            result = breaker.call(lambda: "Recovered!")
            print(f"   ✅ {result}")
        except Exception as e:
            print(f"   ❌ Recovery failed: {e}")
    
    def rate_limiting_demo(self):
        """Demonstrate rate limiting."""
        print("\n🔄 Rate Limiting Demo")
        print("-" * 30)
        
        limiter = RateLimiter(max_requests=3, window_seconds=3)
        
        print("Testing rate limits...")
        for i in range(5):
            allowed = limiter.is_allowed()
            status = "✅ Allowed" if allowed else "❌ Blocked"
            print(f"   Request {i+1}: {status}")
            time.sleep(0.5)
        
        print("\nWaiting for reset...")
        time.sleep(3.1)
        allowed = limiter.is_allowed()
        print(f"   After reset: {'✅ Allowed' if allowed else '❌ Blocked'}")
    
    def validation_demo(self):
        """Demonstrate input validation."""
        print("\n🧪 Input Validation Demo")
        print("-" * 30)
        
        test_cases = [
            ("Valid prompt", "Create a course about Python programming"),
            ("Empty prompt", ""),
            ("Malicious prompt", "<script>alert('hack')</script>Hello World"),
            ("Long prompt", "x" * 5000),
        ]
        
        for name, prompt in test_cases:
            try:
                validated = InputValidator.validate_prompt(prompt)
                print(f"   ✅ {name}: {validated[:50]}...")
            except ValidationError as e:
                print(f"   ❌ {name}: {e}")
    
    def cache_demo(self):
        """Demonstrate cache management."""
        print("\n🧹 Cache Management")
        print("-" * 30)
        
        # Cache stats
        stats = cache_manager.get_stats()
        print(f"Cache entries: {stats.get('total_entries', 0)}")
        print(f"Cache size: {stats.get('total_size_formatted', '0 B')}")
        
        # Clear cache
        cleared = cache_manager.clear()
        print(f"Cleared {cleared} cache entries")
        
        # Test cache operations
        cache_manager.set("test_key", "test_value", ttl=60)
        value = cache_manager.get("test_key")
        print(f"Cache test: {'✅ Working' if value else '❌ Failed'}")
    
    def system_status(self):
        """Show system status."""
        print("\n📊 System Status")
        print("-" * 30)
        
        # Basic system info
        print(f"Python version: {sys.version.split()[0]}")
        print(f"Working directory: {os.getcwd()}")
        print(f"Cache directory: {cache_manager.cache_dir}")
        
        # Check if directories exist
        dirs = ['_output', 'demo_output', '.cache']
        for dir_name in dirs:
            exists = os.path.exists(dir_name)
            print(f"{dir_name}: {'✅ Exists' if exists else '❌ Missing'}")
    
    def run_tests(self):
        """Run basic tests."""
        print("\n🧪 Running Basic Tests")
        print("-" * 30)
        
        tests = [
            ("Configuration", self.config_check),
            ("Security", self.security_demo),
            ("Circuit Breaker", self.circuit_breaker_demo),
            ("Rate Limiting", self.rate_limiting_demo),
            ("Validation", self.validation_demo),
            ("Cache", self.cache_demo),
            ("System Status", self.system_status),
        ]
        
        for name, test_func in tests:
            try:
                print(f"\n{name} test...")
                test_func()
                print(f"✅ {name} completed")
            except Exception as e:
                print(f"❌ {name} failed: {e}")
    
    def run(self):
        """Run the application."""
        print("🎓 AI Course Generator - Simple Runner")
        print("=" * 50)
        
        while True:
            self.display_menu()
            
            try:
                choice = input("\nEnter your choice (0-8): ").strip()
                
                if choice == "1":
                    self.config_check()
                elif choice == "2":
                    self.security_demo()
                elif choice == "3":
                    self.circuit_breaker_demo()
                elif choice == "4":
                    self.rate_limiting_demo()
                elif choice == "5":
                    self.validation_demo()
                elif choice == "6":
                    self.cache_demo()
                elif choice == "7":
                    self.system_status()
                elif choice == "8":
                    self.run_tests()
                elif choice == "0":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main application entry point."""
    app = SimpleApp()
    app.run()

if __name__ == "__main__":
    main()