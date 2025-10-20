#!/usr/bin/env python3
"""
Centralized configuration management for the AI-powered course content generation system.

This module provides a centralized way to manage all configuration settings,
API keys, and constants used throughout the application.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from exceptions import ConfigurationError

load_dotenv()

class Config:
    """Centralized configuration management class."""
    
    # API Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY")
    
    # Validate required environment variables
    @classmethod
    def validate_config(cls) -> None:
        """Validate that all required environment variables are set."""
        required_vars = {
            "OPENROUTER_API_KEY": cls.OPENROUTER_API_KEY,
            "RUNWARE_API_KEY": cls.RUNWARE_API_KEY
        }
        
        missing_vars = [key for key, value in required_vars.items() if not value]
        if missing_vars:
            raise ConfigurationError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
    
    # LLM Configuration
    DEFAULT_MODEL = "google/gemini-2.5-flash-lite-preview-06-17"
    FALLBACK_MODEL = "google/gemini-2.0-flash-001"
    MAX_TOKENS = 260000
    TEMPERATURE = 1.0
    
    # File Paths
    CURRENT_DIRECTORY_FILE = "current_directory.txt"
    OUTLINE_FILE = "course_outline.txt"
    OUTPUT_PPTX = "course_presentation.pptx"
    OUTPUT_MARKDOWN = "course_presentation.md"
    ENHANCED_NOTES_FILE = "06_Enhanced_Notes.txt"
    
    # Directory Structure
    OUTPUT_BASE_DIR = "_output"
    SLIDE_IMAGES_DIR = "slide_images"
    AUDIO_DIR = "audio"
    VIDEO_DIR = "video"
    TEMP_VIDEOS_DIR = "temp_videos"
    QUIZZES_DIR = "quizzes"
    EXAMS_DIR = "exams"
    
    # Image Generation
    IMAGE_WIDTH = 1024
    IMAGE_HEIGHT = 512
    IMAGE_BATCH_SIZE = 25
    
    # Slide Generation Limits
    MAX_SLIDES_TO_PROCESS = 50
    
    # Colors (RGB tuples)
    COLORS = {
        "module_title": (0, 32, 96),      # Dark blue
        "topic_title": (0, 112, 192),    # Medium blue
        "subtopic_title": (0, 176, 240), # Light blue
        "bullet_text": (0, 0, 0),         # Black
        "background": (255, 255, 255),    # White
        "title": (0, 68, 129),            # Cisco Blue
        "accent1": (0, 155, 229),        # Light blue
        "accent2": (100, 195, 84),       # Green
        "accent3": (206, 59, 50)         # Red/orange
    }
    
    # Title Slide Image
    TITLE_IMAGE_WIDTH = 1600
    TITLE_IMAGE_HEIGHT = 900
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "course_generator.log"
    
    # Cache Configuration
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    CACHE_DIR = os.getenv("CACHE_DIR", ".cache")
    CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour
    
    # Rate Limiting Configuration
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # 1 hour
    
    # Health Check Configuration
    HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "300"))  # 5 minutes
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
    
    # Monitoring Configuration
    ENABLE_METRICS = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    METRICS_PORT = int(os.getenv("METRICS_PORT", "9090"))
    
    @classmethod
    def get_current_directory(cls) -> Optional[str]:
        """Get the current working directory from configuration file."""
        try:
            if os.path.exists(cls.CURRENT_DIRECTORY_FILE):
                with open(cls.CURRENT_DIRECTORY_FILE, 'r') as f:
                    directory = f.read().strip()
                    if directory:
                        # Create directory if it doesn't exist
                        Path(directory).mkdir(parents=True, exist_ok=True)
                        return directory
        except Exception as e:
            print(f"Error reading current directory: {e}")
        return None
    
    @classmethod
    def get_output_path(cls, filename: str, course_name: Optional[str] = None) -> str:
        """Get the full path for output files."""
        base_dir = cls.get_current_directory() or "."
        
        if course_name:
            course_dir = os.path.join(base_dir, cls.OUTPUT_BASE_DIR, course_name)
            Path(course_dir).mkdir(parents=True, exist_ok=True)
            return os.path.join(course_dir, filename)
        
        return os.path.join(base_dir, filename)
    
    @classmethod
    def get_course_directory(cls, course_name: str) -> str:
        """Get the course-specific directory path."""
        base_dir = cls.get_current_directory() or "."
        course_dir = os.path.join(base_dir, cls.OUTPUT_BASE_DIR, course_name)
        Path(course_dir).mkdir(parents=True, exist_ok=True)
        return course_dir
    
    @classmethod
    def get_cache_path(cls, key: str) -> str:
        """Get the cache file path for a given key."""
        cache_dir = os.path.join(cls.get_current_directory() or ".", cls.CACHE_DIR)
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        return os.path.join(cache_dir, f"{key}.json")
    
    @classmethod
    def load_config_file(cls, filename: str) -> Dict[str, Any]:
        """Load configuration from a JSON file."""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except Exception as e:
            print(f"Error loading config file {filename}: {e}")
            return {}
    
    @classmethod
    def save_config_file(cls, filename: str, config: Dict[str, Any]) -> bool:
        """Save configuration to a JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config file {filename}: {e}")
            return False

# Create a singleton instance
config = Config()