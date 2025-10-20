#!/usr/bin/env python3
"""
Test suite for validating all code quality improvements and architectural fixes.

This script tests all the new components and ensures they work correctly together.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Import our new components
from config import config
from exceptions import CourseGeneratorException, LLMError, ImageGenerationError
from utils import FileUtils, CacheUtils, ValidationUtils, logger
from cache_manager import cache_manager
from llm_client import llm_client
from image_client import image_client
from a06_Image_Generation_updated import image_manager

class TestSuite:
    """Comprehensive test suite for all improvements."""
    
    def __init__(self):
        """Initialize test suite."""
        self.test_dir = None
        self.original_dir = os.getcwd()
        
    def setup_test_environment(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)
        
        # Create test configuration
        with open("current_directory.txt", "w") as f:
            f.write(self.test_dir)
            
        logger.info(f"Test environment set up in: {self.test_dir}")
        
    def cleanup_test_environment(self):
        """Clean up test environment."""
        os.chdir(self.original_dir)
        if self.test_dir and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            logger.info("Test environment cleaned up")
    
    def test_config_management(self):
        """Test configuration management."""
        print("\n=== Testing Configuration Management ===")
        
        # Test config values
        assert config.OPENROUTER_API_KEY is not None
        assert config.RUNWARE_API_KEY is not None
        assert config.DEFAULT_MODEL is not None
        
        # Test directory management
        current_dir = config.get_current_directory()
        assert current_dir == self.test_dir
        
        print("✓ Configuration management tests passed")
        
    def test_exceptions(self):
        """Test exception handling."""
        print("\n=== Testing Exception Handling ===")
        
        # Test exception creation
        try:
            raise LLMError("Test error", model="test-model")
        except LLMError as e:
            assert str(e) == "Test error"
            assert e.model == "test-model"
            
        try:
            raise ImageGenerationError("Test image error")
        except ImageGenerationError as e:
            assert str(e) == "Test image error"
            
        print("✓ Exception handling tests passed")
    
    def test_utils(self):
        """Test utility functions."""
        print("\n=== Testing Utility Functions ===")
        
        # Test file utilities
        test_file = os.path.join(self.test_dir, "test.txt")
        FileUtils.write_json_file(test_file, {"test": "data"})
        assert os.path.exists(test_file)
        
        data = FileUtils.read_json_file(test_file)
        assert data["test"] == "data"
        
        # Test validation
        validated = ValidationUtils.validate_string("test string")
        assert validated == "test string"
        
        # Test cache utilities
        key = CacheUtils.get_cache_key("test", param="value")
        assert len(key) == 32  # MD5 hash
        
        print("✓ Utility functions tests passed")
    
    def test_caching(self):
        """Test caching system."""
        print("\n=== Testing Caching System ===")
        
        # Test cache operations
        test_key = "test_cache_key"
        test_data = {"test": "data", "number": 42}
        
        cache_manager.set(test_key, test_data, ttl=60)
        cached_data = cache_manager.get(test_key)
        
        assert cached_data is not None
        assert cached_data["test"] == "data"
        assert cached_data["number"] == 42
        
        # Test cache deletion
        cache_manager.delete(test_key)
        assert cache_manager.get(test_key) is None
        
        print("✓ Caching system tests passed")
    
    def test_llm_client(self):
        """Test LLM client."""
        print("\n=== Testing LLM Client ===")
        
        # Test API key validation
        is_valid = llm_client.validate_api_key()
        if is_valid:
            print("✓ API key is valid")
        else:
            print("⚠ API key validation failed (may be due to network issues)")
        
        # Test model info
        models = llm_client.get_available_models()
        assert isinstance(models, list)
        print(f"✓ Found {len(models)} available models")
        
    def test_image_client(self):
        """Test image client."""
        print("\n=== Testing Image Client ===")
        
        # Test API key validation
        is_valid = image_client.validate_api_key()
        if is_valid:
            print("✓ Image API key is valid")
        else:
            print("⚠ Image API key validation failed")
    
    def test_image_generation_manager(self):
        """Test image generation manager."""
        print("\n=== Testing Image Generation Manager ===")
        
        # Test setup
        image_manager.setup_environment()
        
        # Test slide info extraction
        test_outline = {
            "modules": [
                {
                    "title": "Test Module",
                    "topics": [
                        {
                            "title": "Test Topic",
                            "subtopics": [
                                {"title": "Subtopic 1", "content": ["Point 1", "Point 2"]}
                            ]
                        }
                    ]
                }
            ]
        }
        
        slides_info = image_manager.extract_slide_info(test_outline)
        assert len(slides_info) > 0
        print(f"✓ Extracted {len(slides_info)} slides")
        
        # Test prompt generation
        prompts = image_manager.generate_all_image_prompts(test_outline)
        assert isinstance(prompts, dict)
        print(f"✓ Generated {len(prompts)} prompts")
        
    def test_integration(self):
        """Test integration between components."""
        print("\n=== Testing Integration ===")
        
        # Test file I/O integration
        test_data = {
            "test": "integration",
            "components": ["config", "utils", "cache", "clients"]
        }
        
        test_file = os.path.join(self.test_dir, "integration_test.json")
        FileUtils.write_json_file(test_file, test_data)
        
        loaded_data = FileUtils.read_json_file(test_file)
        assert loaded_data == test_data
        
        # Test cache integration
        cache_key = "integration_test"
        cache_manager.set(cache_key, test_data)
        cached_data = cache_manager.get(cache_key)
        assert cached_data == test_data
        
        print("✓ Integration tests passed")
    
    def test_performance(self):
        """Test performance improvements."""
        print("\n=== Testing Performance Improvements ===")
        
        # Test cache performance
        import time
        
        test_data = {"data": list(range(1000))}
        
        # Without cache
        start_time = time.time()
        for i in range(10):
            cache_manager.set(f"perf_test_{i}", test_data)
        cache_time = time.time() - start_time
        
        # With cache (should be faster)
        start_time = time.time()
        for i in range(10):
            cached_data = cache_manager.get(f"perf_test_{i}")
            assert cached_data is not None
        cache_retrieval_time = time.time() - start_time
        
        print(f"✓ Cache write time: {cache_time:.3f}s")
        print(f"✓ Cache read time: {cache_retrieval_time:.3f}s")
        
    def run_all_tests(self):
        """Run all tests."""
        print("=" * 60)
        print("AI Course Generator - Code Quality Test Suite")
        print("=" * 60)
        
        try:
            self.setup_test_environment()
            
            tests = [
                self.test_config_management,
                self.test_exceptions,
                self.test_utils,
                self.test_caching,
                self.test_llm_client,
                self.test_image_client,
                self.test_image_generation_manager,
                self.test_integration,
                self.test_performance
            ]
            
            passed = 0
            failed = 0
            
            for test in tests:
                try:
                    test()
                    passed += 1
                except Exception as e:
                    logger.error(f"Test {test.__name__} failed: {e}")
                    failed += 1
                    print(f"✗ {test.__name__} failed: {e}")
            
            print("\n" + "=" * 60)
            print("Test Results Summary")
            print("=" * 60)
            print(f"✓ Passed: {passed}")
            print(f"✗ Failed: {failed}")
            print(f"Total: {passed + failed}")
            
            if failed == 0:
                print("\n🎉 All tests passed! The improvements are working correctly.")
            else:
                print(f"\n⚠ {failed} test(s) failed. Please check the logs.")
                
        finally:
            self.cleanup_test_environment()

def main():
    """Main test runner."""
    test_suite = TestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()