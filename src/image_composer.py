"""
Image composer module for CardForge.
Handles combining images and text into profile cards.
"""

from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, Tuple, Optional
import textwrap
import os


class ImageComposer:
    """Composes profile cards from images and text."""
    
    def __init__(self, card_width: int = 800, card_height: int = 600):
        """
        Initialize the image composer.
        
        Args:
            card_width: Width of the output card in pixels
            card_height: Height of the output card in pixels
        """
        self.card_width = card_width
        self.card_height = card_height
        self.headshot_size = (200, 200)
        self.margin = 20
        self.section_spacing = 15
        
        # Colors
        self.bg_color = (245, 245, 245)  # Light gray
        self.title_bg_color = (70, 130, 180)  # Steel blue
        self.text_color = (51, 51, 51)  # Dark gray
        self.title_text_color = (255, 255, 255)  # White
        
        # Try to load fonts
        self.title_font = self._load_font(size=24, bold=True)
        self.heading_font = self._load_font(size=16, bold=True)
        self.body_font = self._load_font(size=12)
        self.small_font = self._load_font(size=10)
    
    def _load_font(self, size: int, bold: bool = False) -> ImageFont.ImageFont:
        """Load a font with fallback to default."""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Arial.ttf",
            "/Windows/Fonts/arial.ttf",
        ]
        
        for path in font_paths:
            try:
                if os.path.exists(path):
                    return ImageFont.truetype(path, size)
            except (OSError, IOError):
                continue
        
        # Fallback to default font
        try:
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def create_card(self, 
                   image_path: str, 
                   profile_data: Dict[str, Any], 
                   summary_text: str) -> Image.Image:
        """
        Create a profile card combining image and text.
        
        Args:
            image_path: Path to the profile image
            profile_data: Parsed profile data from markdown
            summary_text: LLM-processed summary text
            
        Returns:
            PIL Image object of the composed card
        """
        # Create base card
        card = Image.new('RGB', (self.card_width, self.card_height), self.bg_color)
        draw = ImageDraw.Draw(card)
        
        # Draw title bar
        title_height = 60
        draw.rectangle([0, 0, self.card_width, title_height], fill=self.title_bg_color)
        
        # Add title text
        title = profile_data.get('title', 'Professional Profile')
        title_bbox = draw.textbbox((0, 0), title, font=self.title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.card_width - title_width) // 2
        draw.text((title_x, 15), title, fill=self.title_text_color, font=self.title_font)
        
        # Load and resize profile image
        try:
            profile_img = Image.open(image_path)
            profile_img = self._resize_image(profile_img, self.headshot_size)
            
            # Paste profile image
            img_x = self.margin
            img_y = title_height + self.margin
            card.paste(profile_img, (img_x, img_y))
            
        except Exception as e:
            print(f"Warning: Could not load image {image_path}: {e}")
            # Draw placeholder rectangle
            img_x = self.margin
            img_y = title_height + self.margin
            draw.rectangle([img_x, img_y, img_x + self.headshot_size[0], 
                          img_y + self.headshot_size[1]], 
                         fill=(200, 200, 200), outline=(100, 100, 100))
            draw.text((img_x + 50, img_y + 90), "No Image", fill=self.text_color, font=self.body_font)
        
        # Calculate text area
        text_x = img_x + self.headshot_size[0] + self.margin
        text_y = title_height + self.margin
        text_width = self.card_width - text_x - self.margin
        text_height = self.card_height - text_y - self.margin
        
        # Add summary text
        self._draw_text_section(draw, "AI Summary", summary_text, 
                              text_x, text_y, text_width)
        
        # Add additional sections if space allows
        current_y = text_y + 150  # Approximate height for summary section
        
        # Add key sections from profile data
        sections_to_show = ['about', 'key_competencies', 'current_aspirations']
        for section_key in sections_to_show:
            if section_key in profile_data and current_y < self.card_height - 80:
                section_title = section_key.replace('_', ' ').title()
                section_content = profile_data[section_key]
                
                # Truncate content if too long
                if len(section_content) > 200:
                    section_content = section_content[:200] + "..."
                
                section_height = self._draw_text_section(
                    draw, section_title, section_content,
                    text_x, current_y, text_width, max_lines=3
                )
                current_y += section_height + self.section_spacing
        
        return card
    
    def _resize_image(self, img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Resize image while maintaining aspect ratio."""
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # Create a new image with the target size and paste the resized image
        new_img = Image.new('RGB', target_size, (255, 255, 255))
        
        # Center the image
        x = (target_size[0] - img.width) // 2
        y = (target_size[1] - img.height) // 2
        
        new_img.paste(img, (x, y))
        return new_img
    
    def _draw_text_section(self, 
                          draw: ImageDraw.Draw, 
                          title: str, 
                          content: str,
                          x: int, 
                          y: int, 
                          width: int, 
                          max_lines: Optional[int] = None) -> int:
        """
        Draw a text section with title and content.
        
        Args:
            draw: ImageDraw object
            title: Section title
            content: Section content
            x, y: Position to draw
            width: Available width
            max_lines: Maximum number of lines for content
            
        Returns:
            Height of the drawn section
        """
        current_y = y
        
        # Draw title
        draw.text((x, current_y), title, fill=self.text_color, font=self.heading_font)
        current_y += 25
        
        # Draw content
        # Handle bullet points
        if '•' in content:
            lines = content.split('\n')
        else:
            # Wrap text
            chars_per_line = width // 8  # Approximate characters per line
            lines = textwrap.wrap(content, width=chars_per_line)
        
        # Limit lines if specified
        if max_lines:
            lines = lines[:max_lines]
        
        for line in lines:
            if current_y > self.card_height - 30:  # Stop if near bottom
                break
            draw.text((x, current_y), line, fill=self.text_color, font=self.body_font)
            current_y += 18
        
        return current_y - y
    
    def save_card(self, card: Image.Image, output_path: str):
        """Save the card to a file."""
        card.save(output_path, 'PNG', quality=95)
        print(f"Card saved to: {output_path}")
    
    def get_card_info(self) -> Dict[str, Any]:
        """Get information about card dimensions and settings."""
        return {
            "card_size": (self.card_width, self.card_height),
            "headshot_size": self.headshot_size,
            "colors": {
                "background": self.bg_color,
                "title_background": self.title_bg_color,
                "text": self.text_color,
                "title_text": self.title_text_color
            }
        }