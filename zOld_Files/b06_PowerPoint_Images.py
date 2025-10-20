#!/usr/bin/env python3
"""
Runware Image Generation Module

This module provides functions to generate and download images using the Runware API.
It can be imported and used by other Python files.
"""

import asyncio
import os
import aiohttp
from typing import List, Optional
from runware import Runware, IImageInference

# Default API key - you can override this when calling generate_image
RUNWARE_API_KEY = "63vsF4qW47KsCTWSRdTZdZrZMi0Sq4Gk"

# Create default directory to save images
DEFAULT_IMAGE_DIR = "generated_images"
os.makedirs(DEFAULT_IMAGE_DIR, exist_ok=True)

async def download_image(session, image_url: str, filename: str) -> bool:
    """Download image from URL and save it to a file."""
    try:
        async with session.get(image_url) as response:
            if response.status == 200:
                image_data = await response.read()
                with open(filename, 'wb') as f:
                    f.write(image_data)
                print(f"Downloaded image to: {filename}")
                return True
            else:
                print(f"Failed to download image: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return False

async def generate_and_download_image(
    prompt: str,
    output_path: str,
    model: str = "civitai:36520@76907",
    negative_prompt: str = "",
    width: int = 512,
    height: int = 512,
    num_images: int = 1,
    api_key: str = RUNWARE_API_KEY,
) -> List[str]:
    """Generate images using Runware API and download them.
    
    Args:
        prompt: The text prompt for image generation
        output_path: Full path where image will be saved
        model: Runware model ID to use
        negative_prompt: Things to avoid in the image
        width: Image width in pixels
        height: Image height in pixels
        num_images: Number of images to generate
        api_key: Runware API key
        
    Returns:
        List of paths to the downloaded images
    """
    # Create directory for the output if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Get filename without extension and directory path
    filename_base = os.path.splitext(os.path.basename(output_path))[0]
    dir_path = os.path.dirname(os.path.abspath(output_path))
    
    # Initialize Runware client
    runware = Runware(api_key=api_key)
    await runware.connect()
    
    # Create image request
    request_image = IImageInference(
        positivePrompt=prompt,
        model=model,
        numberResults=num_images,
        negativePrompt=negative_prompt,
        height=height,
        width=width,
    )
    
    # Generate images
    generated_files = []
    try:
        images = await runware.imageInference(requestImage=request_image)
        
        # Create a single aiohttp session for all downloads
        async with aiohttp.ClientSession() as session:
            for i, image in enumerate(images):
                if num_images == 1:
                    # Use the exact output_path provided for a single image
                    filename = output_path
                else:
                    # Create indexed filenames for multiple images
                    ext = os.path.splitext(output_path)[1] or ".png"  # Default to PNG if no extension
                    filename = os.path.join(dir_path, f"{filename_base}_{i+1}{ext}")
                
                # Download the image
                success = await download_image(session, image.imageURL, filename)
                if success:
                    generated_files.append(filename)
    finally:
        # Always disconnect when done
        await runware.disconnect()
    
    return generated_files

# Synchronous wrapper for easier calling from other code
def generate_image(prompt: str, output_path: str, **kwargs) -> List[str]:
    """Synchronous wrapper around generate_and_download_image.
    
    Args are the same as generate_and_download_image.
    Returns a list of downloaded image file paths.
    """
    return asyncio.run(generate_and_download_image(prompt, output_path, **kwargs))

# Example usage when run directly
if __name__ == "__main__":
    # Example call
    print("Running image generation example...")
    images = generate_image(
        prompt="a beautiful sunset over the mountains",
        output_path=os.path.join(DEFAULT_IMAGE_DIR, "example_sunset.png"),
        negative_prompt="cloudy, rainy",
        num_images=1
    )
    print(f"Generated and saved {len(images)} images.")