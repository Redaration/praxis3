#!/usr/bin/env python3
"""
Runware Image Generation Module

This module provides functions to generate and download images using the Runware API.
It can be imported and used by other Python files.

Usage:
    from arunware_image_generator import generate_image, generate_images_parallel
    
    # For a single image:
    single_image = generate_image("a prompt", "path/to/image.png")

    # For multiple images in parallel:
    image_requests = [("prompt1", "path1.png"), ("prompt2", "path2.png")]
    multiple_images = generate_images_parallel(image_requests)
"""

import asyncio
import os
import aiohttp
from typing import List, Optional
from runware import Runware, IImageInference
from dotenv import load_dotenv

load_dotenv()

# Load API key from environment variable
RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY")

# Create default directory to save images
DEFAULT_IMAGE_DIR = "generated_images"
os.makedirs(DEFAULT_IMAGE_DIR, exist_ok=True)

# Default negative prompt enforced to satisfy Runware API requirements
DEFAULT_NEGATIVE_PROMPT = "text, watermark, logo"

async def download_image(session, image_url: str, filename: str) -> bool:
    """Download image from URL and save it to a file."""
    try:
        async with session.get(image_url) as response:
            if response.status == 200:
                image_data = await response.read()
                with open(filename, 'wb') as f:
                    f.write(image_data)
                print(f"2 -Downloaded image to: {filename}")
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
    model: str = "runware:100@1",
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
    # Process request
    # Ensure the negative prompt meets API requirements (2-3000 characters)
    negative_prompt_value = str(negative_prompt or "").strip()
    if len(negative_prompt_value) < 2:
        negative_prompt_value = DEFAULT_NEGATIVE_PROMPT

    # Create image request
    request_image = IImageInference(
        positivePrompt=prompt+". No Text in the image",
        model=model,
        numberResults=num_images,
        negativePrompt=negative_prompt_value,
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
                    ext = os.path.splitext(output_path)[1] or ".png"
                    filename = os.path.join(dir_path, f"{filename_base}_{i+1}{ext}")
                
                # Download the image
                success = await download_image(session, image.imageURL, filename)
                if success:
                    generated_files.append(filename)
    finally:
        # Try to disconnect if the method exists
        try:
            # Check if disconnect method exists
            if hasattr(runware, 'disconnect'):
                await runware.disconnect()
        except Exception as e:
            print(f"Note: Could not disconnect from Runware API: {str(e)}")
            # Continue execution - this is not a critical error
    
    return generated_files

# Synchronous wrapper for easier calling from other code
def generate_image(prompt: str, output_path: str, **kwargs) -> List[str]:
    """Synchronous wrapper around generate_and_download_image.
    
    Args are the same as generate_and_download_image.
    Returns a list of downloaded image file paths.
    """
    return asyncio.run(generate_and_download_image(prompt, output_path, **kwargs))


async def generate_multiple_images_parallel(prompts_and_paths: List[tuple], **kwargs) -> List[str]:
    """
    Generate images for multiple slides in parallel using Runware's task-based architecture.
    
    Args:
        prompts_and_paths: List of (prompt, output_path) tuples for each slide
        **kwargs: Additional arguments for image generation (model, width, height, etc.)
        
    Returns:
        List of paths to all downloaded images
    """
    if not prompts_and_paths:
        return []
        
    # Initialize Runware client
    api_key = kwargs.get('api_key', RUNWARE_API_KEY)
    runware = Runware(api_key=api_key)
    await runware.connect()
    
    # Get common parameters for all requests
    model = kwargs.get('model', "runware:100@1")
    negative_prompt = kwargs.get('negative_prompt', "")
    width = kwargs.get('width', 512)
    height = kwargs.get('height', 512)
    num_images = kwargs.get('num_images', 1)  # Images per slide prompt
    
    # Create directory for each output path
    for _, output_path in prompts_and_paths:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Prepare all image requests
    all_requests = []
    for prompt, _ in prompts_and_paths:
        # Ensure the negative prompt meets API requirements (2-3000 characters)
        negative_prompt_value = str(negative_prompt or "").strip()
        if len(negative_prompt_value) < 2:
            negative_prompt_value = DEFAULT_NEGATIVE_PROMPT

        request = IImageInference(
            positivePrompt=prompt+". No Text in the image",
            model=model,
            numberResults=num_images,
            negativePrompt=negative_prompt_value,
            height=height,
            width=width,
        )
        all_requests.append(request)
    
    # Generate all images in parallel
    generated_files = []
    try:
        # Send all requests simultaneously
        all_results = await asyncio.gather(*[runware.imageInference(requestImage=req) for req in all_requests])
        
        # Create a single aiohttp session for all downloads
        async with aiohttp.ClientSession() as session:
            # Process each slide's results
            for i, (images, (_, output_path)) in enumerate(zip(all_results, prompts_and_paths)):
                filename_base = os.path.splitext(os.path.basename(output_path))[0]
                dir_path = os.path.dirname(os.path.abspath(output_path))
                
                # Download each image for this slide
                for j, image in enumerate(images):
                    if num_images == 1:
                        filename = output_path
                    else:
                        ext = os.path.splitext(output_path)[1] or ".png"
                        filename = os.path.join(dir_path, f"{filename_base}_{j+1}{ext}")
                    
                    # Download the image
                    success = await download_image(session, image.imageURL, filename)
                    if success:
                        generated_files.append(filename)
                    
                print(f"1 - Generated {len(images)} image(s) for prompt {i+1}/{len(prompts_and_paths)}")
    finally:
        # Try to disconnect if the method exists
        try:
            if hasattr(runware, 'disconnect'):
                await runware.disconnect()
        except Exception as e:
            print(f"Note: Could not disconnect from Runware API: {str(e)}")
    
    return generated_files


def generate_images_parallel(prompts_and_paths: List[tuple], **kwargs) -> List[str]:
    """Synchronous wrapper around generate_multiple_images_parallel.
    
    Args:
        prompts_and_paths: List of (prompt, output_path) tuples for each slide
        **kwargs: Additional arguments for image generation
        
    Returns:
        List of downloaded image file paths
    """
    return asyncio.run(generate_multiple_images_parallel(prompts_and_paths, **kwargs))
