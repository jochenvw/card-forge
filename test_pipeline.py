#!/usr/bin/env python3
"""
Simple test script to validate CardForge pipeline functionality.
"""

import os
import sys
import tempfile
from PIL import Image

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.markdown_parser import MarkdownParser
from src.llm_processor import LLMProcessor
from src.image_composer import ImageComposer


def test_markdown_parser():
    """Test markdown parsing functionality."""
    print("Testing Markdown Parser...")
    
    # Create test markdown content
    test_content = """# Test Profile

## Skills
- Python Programming
- Machine Learning
- Data Science

## Goals
- Build great software
- Lead engineering teams

## About
Experienced software engineer.
"""
    
    parser = MarkdownParser()
    result = parser.parse_content(test_content)
    
    expected_sections = ['title', 'skills', 'goals', 'about']
    for section in expected_sections:
        assert section in result, f"Missing section: {section}"
    
    assert result['title'] == "Test Profile"
    assert "Python Programming" in result['skills']
    print("✅ Markdown Parser tests passed")


def test_llm_processor():
    """Test LLM processor functionality."""
    print("Testing LLM Processor...")
    
    processor = LLMProcessor()
    
    test_text = """Profile: John Doe

Key Competencies:
- Python Development: Expert-level proficiency
- Machine Learning: Experience with PyTorch
- Cloud Technologies: AWS, Docker experience

Current Aspirations:
- Leading ML engineering teams
- Contributing to open-source projects"""
    
    result = processor.summarize_profile(test_text)
    
    assert len(result) > 0, "Summary should not be empty"
    assert "•" in result, "Summary should contain bullet points"
    print("✅ LLM Processor tests passed")


def test_image_composer():
    """Test image composition functionality."""
    print("Testing Image Composer...")
    
    composer = ImageComposer(card_width=400, card_height=300)
    
    # Create a test image
    test_img = Image.new('RGB', (100, 100), color='red')
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        test_img.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        profile_data = {
            'title': 'Test Profile',
            'about': 'Test description',
            'key_competencies': 'Test skills'
        }
        
        summary_text = "• Test skill 1\n• Test skill 2"
        
        card = composer.create_card(tmp_path, profile_data, summary_text)
        
        assert card.size == (400, 300), f"Card size mismatch: {card.size}"
        print("✅ Image Composer tests passed")
        
    finally:
        os.unlink(tmp_path)


def test_full_pipeline():
    """Test the complete pipeline."""
    print("Testing Full Pipeline...")
    
    # Check if example files exist
    example_image = "examples/input_photo.png"
    example_markdown = "examples/profile.md"
    
    if not os.path.exists(example_image):
        print(f"⚠️  Example image not found: {example_image}")
        return
    
    if not os.path.exists(example_markdown):
        print(f"⚠️  Example markdown not found: {example_markdown}")
        return
    
    # Test the pipeline components
    parser = MarkdownParser()
    processor = LLMProcessor()
    composer = ImageComposer()
    
    # Parse markdown
    profile_data = parser.parse_file(example_markdown)
    assert 'title' in profile_data
    
    # Extract key content
    key_content = parser.extract_key_points(profile_data)
    assert len(key_content) > 0
    
    # Process with LLM
    summary_text = processor.summarize_profile(key_content)
    assert len(summary_text) > 0
    
    # Create card
    card = composer.create_card(example_image, profile_data, summary_text)
    assert card.size == (800, 600)
    
    print("✅ Full pipeline tests passed")


def main():
    """Run all tests."""
    print("🧪 Running CardForge Tests...\n")
    
    try:
        test_markdown_parser()
        test_llm_processor()
        test_image_composer()
        test_full_pipeline()
        
        print("\n🎉 All tests passed! CardForge is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()