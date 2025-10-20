#!/usr/bin/env python3
"""
Enhanced Image Generation Client with Caching, Retry Logic, and Parallel Processing

This module provides a robust interface for generating AI images using the Runware API,
with built-in caching, retry mechanisms, and parallel processing capabilities.

THIRD-PARTY SERVICES:
    - Runware AI: AI-powered image generation service
      Website: https://runware.ai/
      Documentation: https://docs.runware.ai/
      License: Commercial API service (requires API key)
      Purpose: Generate high-quality images from text prompts for educational content

THIRD-PARTY LIBRARIES:
    - runware: Official Runware Python SDK
      License: Proprietary/Commercial
      PyPI: https://pypi.org/project/runware/
      Documentation: https://docs.runware.ai/

    - requests: HTTP library for downloading generated images
      License: Apache 2.0
      PyPI: https://pypi.org/project/requests/

    - aiohttp: Asynchronous HTTP client/server
      License: Apache 2.0
      PyPI: https://pypi.org/project/aiohttp/

DESIGN PATTERNS:
    - Circuit Breaker: Handles API failures gracefully
    - Retry with Exponential Backoff: Manages transient network issues
    - Thread Pool Executor: Enables parallel image generation
    - Async/Await: Efficient concurrent operations
    - Caching: Reduces duplicate API calls for same prompts

ACADEMIC CONTEXT:
    This client generates educational images for course presentations, including:
    - Slide backgrounds and visual aids
    - Conceptual diagrams and illustrations
    - Title slides and module headers
    All generated images should be reviewed for educational appropriateness.

IMPORTANT NOTES:
    - Image generation is computationally expensive and metered
    - Default dimensions: 1024x512 pixels (configurable)
    - Parallel processing improves performance for batch operations
    - Cache reduces costs for repeated prompts

Author: Brandon Yohn
Institution: The George Washington University
Program: Praxis Doctoral Program
Last Modified: 2025-01-20

See ATTRIBUTIONS.md for complete library and service attributions.
"""

import os
import asyncio
import aiohttp  # Apache 2.0 License
from typing import List, Dict, Any, Optional, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

import os
import time
from config import config
from exceptions import ImageGenerationError, RateLimitError, NetworkError
from cache_manager import cached, cache_manager
from utils import RetryUtils, FileUtils, logger
from rate_limiter import image_rate_limiter
from circuit_breaker import circuit_breaker
from metrics import metrics_collector

class ImageClient:
    """Enhanced image generation client with caching and parallel processing."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the image client."""
        config.validate_config()
        self.api_key = api_key or config.RUNWARE_API_KEY
        self.base_url = "https://api.runware.ai/v1"
        
    @RetryUtils.retry(max_attempts=3, delay=2.0)
    @circuit_breaker(
        failure_threshold=config.CIRCUIT_BREAKER_THRESHOLD,
        recovery_timeout=config.HEALTH_CHECK_INTERVAL
    )
    def generate_image(
        self,
        prompt: str,
        width: int = None,
        height: int = None,
        num_images: int = 1,
        **kwargs
    ) -> List[str]:
        """
        Generate a single image with retry logic.
        
        Args:
            prompt: Image generation prompt
            width: Image width (default: config.IMAGE_WIDTH)
            height: Image height (default: config.IMAGE_HEIGHT)
            num_images: Number of images to generate
            **kwargs: Additional parameters
            
        Returns:
            List of generated image URLs
        """
        width = width or config.IMAGE_WIDTH
        height = height or config.IMAGE_HEIGHT
        
        start_time = time.time()
        try:
            image_rate_limiter.check_rate_limit()
            
            try:
                import runware
                from runware.types import RequestImage
            except ImportError:
                raise ImageGenerationError(
                    "runware package not installed. Install with: pip install runware"
                )
            
            # Initialize Runware client
            runware_client = runware.Runware(api_key=self.api_key)
            
            # Create image request
            request_image = RequestImage(
                prompt=prompt,
                width=width,
                height=height,
                numberResults=num_images,
                **kwargs
            )
            
            # Generate image
            images = runware_client.imageInference(requestImage=request_image)
            
            if not images:
                raise ImageGenerationError("No images generated")
            
            duration = time.time() - start_time
            metrics_collector.record_image_generation(duration)
            
            return [image.imageURL for image in images]
            
        except Exception as e:
            duration = time.time() - start_time
            metrics_collector.record_image_generation(duration, str(e))
            
            if "rate limit" in str(e).lower():
                raise RateLimitError("Image generation rate limit exceeded")
            raise ImageGenerationError(f"Image generation failed: {e}")
    
    @cached(ttl=3600)  # Cache for 1 hour
    def generate_image_cached(
        self,
        prompt: str,
        width: int = None,
        height: int = None,
        **kwargs
    ) -> List[str]:
        """Cached version of generate_image."""
        return self.generate_image(prompt, width, height, **kwargs)
    
    def generate_images_parallel(
        self,
        prompts: List[str],
        width: int = None,
        height: int = None,
        max_workers: int = 5,
        **kwargs
    ) -> List[str]:
        """
        Generate multiple images in parallel.
        
        Args:
            prompts: List of prompts
            width: Image width
            height: Image height
            max_workers: Maximum parallel workers
            **kwargs: Additional parameters
            
        Returns:
            List of generated image URLs
        """
        width = width or config.IMAGE_WIDTH
        height = height or config.IMAGE_HEIGHT
        
        logger.info(f"Generating {len(prompts)} images in parallel")
        
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_prompt = {
                executor.submit(
                    self.generate_image_cached,
                    prompt,
                    width,
                    height,
                    **kwargs
                ): prompt
                for prompt in prompts
            }
            
            # Collect results
            for future in as_completed(future_to_prompt):
                prompt = future_to_prompt[future]
                try:
                    image_urls = future.result()
                    results.extend(image_urls)
                    logger.debug(f"Generated image for prompt: {prompt[:50]}...")
                except Exception as e:
                    logger.error(f"Failed to generate image for prompt: {prompt[:50]}... Error: {e}")
                    results.append(None)
        
        return results
    
    async def generate_images_async(
        self,
        prompts: List[str],
        width: int = None,
        height: int = None,
        **kwargs
    ) -> List[str]:
        """
        Generate images asynchronously.
        
        Args:
            prompts: List of prompts
            width: Image width
            height: Image height
            **kwargs: Additional parameters
            
        Returns:
            List of generated image URLs
        """
        width = width or config.IMAGE_WIDTH
        height = height or config.IMAGE_HEIGHT
        
        async def generate_single(prompt: str) -> List[str]:
            try:
                return await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.generate_image,
                    prompt,
                    width,
                    height,
                    **kwargs
                )
            except Exception as e:
                logger.error(f"Failed to generate image: {e}")
                return []
        
        # Process in batches
        batch_size = min(config.IMAGE_BATCH_SIZE, len(prompts))
        results = []
        
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            tasks = [generate_single(prompt) for prompt in batch]
            batch_results = await asyncio.gather(*tasks)
            
            for urls in batch_results:
                results.extend(urls)
        
        return results
    
    def download_image(self, url: str, output_path: str) -> bool:
        """Download an image from URL to local file."""
        try:
            import requests
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            FileUtils.ensure_directory(os.path.dirname(output_path))
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.debug(f"Downloaded image: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return False
    
    def download_images_parallel(
        self,
        urls: List[str],
        output_dir: str,
        max_workers: int = 5
    ) -> List[str]:
        """Download multiple images in parallel."""
        downloaded_files = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {}
            
            for i, url in enumerate(urls):
                filename = f"image_{i+1:03d}.png"
                output_path = os.path.join(output_dir, filename)
                
                future = executor.submit(self.download_image, url, output_path)
                future_to_url[future] = (url, output_path)
            
            for future in as_completed(future_to_url):
                url, output_path = future_to_url[future]
                try:
                    success = future.result()
                    if success:
                        downloaded_files.append(output_path)
                except Exception as e:
                    logger.error(f"Failed to download {url}: {e}")
        
        return downloaded_files
    
    def validate_api_key(self) -> bool:
        """Validate the API key by making a test request."""
        try:
            self.generate_image(
                prompt="Test image generation",
                width=256,
                height=256,
                num_images=1
            )
            return True
        except Exception as e:
            logger.error(f"API validation failed: {e}")
            return False

# Global client instance
image_client = ImageClient()

# Convenience functions
def generate_image(
    prompt: str,
    width: int = None,
    height: int = None,
    **kwargs
) -> List[str]:
    """Convenience function to generate image with global client."""
    return image_client.generate_image(prompt, width, height, **kwargs)

def generate_images_parallel(
    prompts: List[str],
    width: int = None,
    height: int = None,
    **kwargs
) -> List[str]:
    """Convenience function for parallel image generation."""
    return image_client.generate_images_parallel(prompts, width, height, **kwargs)

# Export commonly used items
__all__ = [
    'ImageClient', 'image_client', 'generate_image', 'generate_images_parallel'
]