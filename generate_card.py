#!/usr/bin/env python3
"""
CardForge MVP - Profile Card Generator

Generates beautiful profile cards from images and markdown descriptions
using local LLM processing.

Usage:
    python generate_card.py --image input_photo.png --markdown profile.md --output output_card.png
"""

import argparse
import os
import sys
from typing import Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.markdown_parser import MarkdownParser
from src.llm_processor import LLMProcessor
from src.image_composer import ImageComposer


def main():
    """Main function for the CardForge CLI."""
    parser = argparse.ArgumentParser(
        description="Generate profile cards from images and markdown descriptions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_card.py --image photo.png --markdown profile.md --output card.png
  python generate_card.py -i examples/input_photo.png -m examples/profile.md -o output/my_card.png
        """
    )
    
    parser.add_argument(
        '--image', '-i',
        required=True,
        help='Path to the input image (PNG recommended)'
    )
    
    parser.add_argument(
        '--markdown', '-m',
        required=True,
        help='Path to the markdown profile file'
    )
    
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Path for the output card image (PNG)'
    )
    
    parser.add_argument(
        '--model',
        default='microsoft/DialoGPT-medium',
        help='LLM model to use for text processing (default: microsoft/DialoGPT-medium)'
    )
    
    parser.add_argument(
        '--width',
        type=int,
        default=800,
        help='Card width in pixels (default: 800)'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=600,
        help='Card height in pixels (default: 600)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}")
        sys.exit(1)
    
    if not os.path.exists(args.markdown):
        print(f"Error: Markdown file not found: {args.markdown}")
        sys.exit(1)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        if args.verbose:
            print(f"Created output directory: {output_dir}")
    
    try:
        # Initialize components
        if args.verbose:
            print("Initializing CardForge components...")
        
        markdown_parser = MarkdownParser()
        llm_processor = LLMProcessor(model_name=args.model)
        image_composer = ImageComposer(card_width=args.width, card_height=args.height)
        
        # Display device info
        if args.verbose:
            device_info = llm_processor.get_device_info()
            print(f"Device: {device_info['device']}")
            print(f"CUDA available: {device_info['cuda_available']}")
            print(f"Model: {device_info['model_name']}")
            print(f"Model loaded: {device_info['model_loaded']}")
        
        # Step 1: Parse markdown
        if args.verbose:
            print(f"Parsing markdown file: {args.markdown}")
        
        profile_data = markdown_parser.parse_file(args.markdown)
        
        if args.verbose:
            print(f"Found sections: {list(profile_data.keys())}")
        
        # Step 2: Extract key content for LLM
        key_content = markdown_parser.extract_key_points(profile_data)
        
        if args.verbose:
            print("Extracted key content for LLM processing:")
            print(key_content[:200] + "..." if len(key_content) > 200 else key_content)
        
        # Step 3: Process with LLM
        if args.verbose:
            print("Processing text with LLM...")
        
        summary_text = llm_processor.summarize_profile(key_content)
        
        if args.verbose:
            print("LLM Summary:")
            print(summary_text)
        
        # Step 4: Compose the card
        if args.verbose:
            print(f"Composing card with image: {args.image}")
        
        card_image = image_composer.create_card(args.image, profile_data, summary_text)
        
        # Step 5: Save the result
        image_composer.save_card(card_image, args.output)
        
        print(f"✅ Profile card generated successfully: {args.output}")
        
        # Display card info
        if args.verbose:
            card_info = image_composer.get_card_info()
            print(f"Card dimensions: {card_info['card_size']}")
    
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error generating card: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()