#!/usr/bin/env python3
"""
Test script to demonstrate how to use the Runware image generator with PowerPoint slides

Usage:
    To run the test script:
        python atest_runware_integration.py
    
    To use as a module:
        from atest_runware_integration import test_generate_slide_image
        test_generate_slide_image()
"""

import os
from runware_image_generator import generate_image

def test_generate_slide_image():
    """Test generating an image for a PowerPoint slide"""
    
    # Sample slide content
    slide_title = "Cisco SASE Architecture Overview"
    slide_content = [
        "Secure connectivity with SD-WAN",
        "Cloud-delivered security with Umbrella",
        "Zero Trust Network Access with Duo"
    ]
    
    # Create output directory if it doesn't exist
    os.makedirs("test_images", exist_ok=True)
    output_path = "test_images/test_sase_image.png"
    
    # Create a prompt from the slide content
    prompt = f"Create a professional, business-appropriate image that represents: {slide_title}"
    context = ". ".join(slide_content)
    prompt += f". The image should relate to these concepts: {context}"
    prompt += ". Style should be professional, clean design, suitable for a corporate presentation."
    
    print(f"Generating image for: {slide_title}")
    print(f"Using prompt: {prompt}")
    
    # Generate the image using Runware
    downloaded_images = generate_image(
        prompt=prompt,
        output_path=output_path,
        width=800,
        height=600,
        negative_prompt="text, watermarks, logos, inappropriate content, low quality"
    )
    
    # Check if image was successfully generated
    if downloaded_images:
        print(f"Success! Image saved to: {downloaded_images[0]}")
    else:
        print("Failed to generate image")

if __name__ == "__main__":
    print("Testing Runware integration for PowerPoint images...")
    test_generate_slide_image()
    print("Done!")
