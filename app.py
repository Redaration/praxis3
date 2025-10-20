#!/usr/bin/env python3
"""
AI Course Generator - Main Application Runner

This is the primary application entry point that demonstrates the complete
AI-powered course content generation system with all enhancements integrated.

SYSTEM OVERVIEW:
    This application generates comprehensive educational course content using AI,
    including PowerPoint presentations, quizzes, exams, images, and multimedia.
    It integrates multiple AI services with production-grade infrastructure.

KEY FEATURES:
    - Health monitoring and system diagnostics
    - Performance metrics collection
    - Input validation and security
    - LLM-powered text generation (via OpenRouter)
    - AI image generation (via Runware)
    - Caching for performance optimization
    - Circuit breaker for fault tolerance
    - Rate limiting for cost control

THIRD-PARTY SERVICES:
    - OpenRouter API: LLM text generation
    - Runware API: AI image generation

DESIGN PATTERNS:
    - Circuit Breaker: Fault tolerance
    - Rate Limiter: API quota management
    - Cache Manager: Performance optimization
    - Health Checker: System monitoring
    - Metrics Collector: Usage tracking

ACADEMIC CONTEXT:
    This application is part of a doctoral research project exploring AI-powered
    educational content generation. It demonstrates how AI can assist in creating
    comprehensive course materials while maintaining quality and consistency.

USAGE:
    python app.py

    The application provides an interactive menu for:
    - Running health checks
    - Viewing system metrics
    - Testing LLM and image generation
    - Running validation tests
    - Managing cache

REQUIREMENTS:
    - Python 3.12+
    - Valid API keys in .env file (OPENROUTER_API_KEY, RUNWARE_API_KEY)
    - Required Python packages (see requirements.txt)

Author: Brandon Yohn
Institution: The George Washington University
Program: Praxis Doctoral Program
Last Modified: 2025-01-20

See ATTRIBUTIONS.md for complete library and service attributions.
"""

import os
import sys
import time
from pathlib import Path

# Import our enhanced components
from config import config
from health_check import health_manager, check_health
from metrics import get_metrics
from validation import validate_prompt, validate_api_key
from llm_client import llm_client
from image_client import image_client
from cache_manager import cache_manager
from circuit_breaker import CircuitBreaker
from rate_limiter import RateLimiter

class CourseGeneratorApp:
    """Main application class for the AI Course Generator."""
    
    def __init__(self):
        """Initialize the application."""
        self.setup_environment()
        self.validate_configuration()
        
    def setup_environment(self):
        """Set up the application environment."""
        print("🚀 Initializing AI Course Generator...")
        
        # Set up current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open("current_directory.txt", "w") as f:
            f.write(current_dir)
        
        print(f"📁 Working directory: {current_dir}")
        
    def validate_configuration(self):
        """Validate the application configuration."""
        try:
            config.validate_config()
            print("✅ Configuration validated successfully")
        except Exception as e:
            print(f"❌ Configuration error: {e}")
            print("\n🔧 Please set up your environment variables:")
            print("   cp .env.example .env")
            print("   # Edit .env with your actual API keys")
            sys.exit(1)
    
    def display_menu(self):
        """Display the main menu."""
        print("\n" + "="*60)
        print("🎓 AI Course Generator - Main Menu")
        print("="*60)
        print("1. 🏥 Health Check")
        print("2. 📊 View Metrics")
        print("3. 💬 Test LLM Client")
        print("4. 🖼️ Test Image Client")
        print("5. 🧪 Run Validation Tests")
        print("6. 🔄 Test Rate Limiting")
        print("7. ⚡ Test Circuit Breaker")
        print("8. 🧹 Clear Cache")
        print("9. 🧪 Run All Tests")
        print("0. ❌ Exit")
        print("="*60)
    
    def health_check(self):
        """Run health checks."""
        print("\n🏥 Running health checks...")
        health = check_health()
        
        print(f"Overall Status: {health['status'].upper()}")
        print("\nComponent Status:")
        for component, status in health['checks'].items():
            status_icon = "✅" if status['healthy'] else "❌"
            print(f"  {status_icon} {component}")
    
    def view_metrics(self):
        """Display current metrics."""
        print("\n📊 Current Metrics:")
        metrics = get_metrics()
        
        print(f"  API Calls: {metrics['api_calls']}")
        print(f"  Cache Hits: {metrics['cache_hits']}")
        print(f"  Cache Misses: {metrics['cache_misses']}")
        print(f"  Error Rate: {metrics['error_rate']:.2%}")
        print(f"  Cache Hit Rate: {metrics['cache_hit_rate']:.2%}")
        print(f"  Uptime: {metrics['uptime_seconds']:.1f}s")
    
    def test_llm_client(self):
        """Test the LLM client."""
        print("\n💬 Testing LLM client...")
        
        try:
            # Validate API key
            is_valid = llm_client.validate_api_key()
            if is_valid:
                print("✅ LLM API key is valid")
                
                # Test with a simple prompt
                prompt = "Explain what artificial intelligence is in one sentence."
                response = llm_client.call_llm(prompt, max_tokens=100)
                print(f"🤖 Response: {response[:100]}...")
            else:
                print("❌ LLM API key validation failed")
                
        except Exception as e:
            print(f"❌ LLM test failed: {e}")
    
    def test_image_client(self):
        """Test the image client."""
        print("\n🖼️ Testing image client...")
        
        try:
            # Validate API key
            is_valid = image_client.validate_api_key()
            if is_valid:
                print("✅ Image API key is valid")
                
                # Test with a simple prompt
                prompt = "A simple educational icon"
                images = image_client.generate_image(prompt, width=256, height=256)
                print(f"✅ Generated {len(images)} image(s)")
                for i, url in enumerate(images):
                    print(f"  Image {i+1}: {url[:50]}...")
            else:
                print("❌ Image API key validation failed")
                
        except Exception as e:
            print(f"❌ Image test failed: {e}")
    
    def test_validation(self):
        """Test input validation."""
        print("\n🧪 Testing validation...")
        
        # Test prompt validation
        try:
            prompt = validate_prompt("Generate a course about Python")
            print(f"✅ Valid prompt: {prompt}")
        except Exception as e:
            print(f"❌ Prompt validation failed: {e}")
        

    
    def test_rate_limiting(self):
        """Test rate limiting."""
        print("\n🔄 Testing rate limiting...")
        
        limiter = RateLimiter(max_requests=3, window_seconds=5)
        
        # Test rapid requests
        for i in range(5):
            allowed = limiter.is_allowed()
            print(f"  Request {i+1}: {'✅ Allowed' if allowed else '❌ Blocked'}")
            time.sleep(0.1)
    
    def test_circuit_breaker(self):
        """Test circuit breaker."""
        print("\n⚡ Testing circuit breaker...")
        
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=1
        )
        
        # Test successful calls
        for i in range(3):
            try:
                result = breaker.call(lambda: "success")
                print(f"  Call {i+1}: ✅ {result}")
            except Exception as e:
                print(f"  Call {i+1}: ❌ {e}")
    
    def clear_cache(self):
        """Clear the cache."""
        print("\n🧹 Clearing cache...")
        cleared = cache_manager.clear()
        print(f"✅ Cleared {cleared} cache entries")
    
    def run_tests(self):
        """Run comprehensive tests."""
        print("\n🧪 Running comprehensive tests...")
        try:
            from enhanced_test_suite import run_comprehensive_tests
            success = run_comprehensive_tests()
            if success:
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed")
        except Exception as e:
            print(f"❌ Test runner failed: {e}")
    
    def run(self):
        """Run the application."""
        print("🎓 AI Course Generator - Enhanced Version")
        print("="*60)
        
        # Initial health check
        self.health_check()
        
        while True:
            self.display_menu()
            
            try:
                choice = input("\nEnter your choice (0-9): ").strip()
                
                if choice == "1":
                    self.health_check()
                elif choice == "2":
                    self.view_metrics()
                elif choice == "3":
                    self.test_llm_client()
                elif choice == "4":
                    self.test_image_client()
                elif choice == "5":
                    self.test_validation()
                elif choice == "6":
                    self.test_rate_limiting()
                elif choice == "7":
                    self.test_circuit_breaker()
                elif choice == "8":
                    self.clear_cache()
                elif choice == "9":
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
    app = CourseGeneratorApp()
    app.run()

if __name__ == "__main__":
    main()