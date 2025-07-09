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
        self.headshot_size = (180, 180)  # Slightly smaller for better proportions
        self.margin = 30  # Increased margin for modern spacing
        self.section_spacing = 20  # More spacing between sections
        self.corner_radius = 15  # Rounded corners
        
        # Modern color palette
        self.bg_color = (255, 255, 255)  # Clean white background
        self.card_bg_color = (250, 251, 252)  # Very subtle gray for card
        self.title_bg_color = (52, 73, 93)  # Modern dark blue-gray
        self.text_color = (44, 62, 80)  # Softer dark gray
        self.title_text_color = (255, 255, 255)  # White
        self.accent_color = (46, 204, 113)  # Modern green accent
        self.section_bg_color = (255, 255, 255)  # White for sections
        self.border_color = (236, 240, 241)  # Light border
        self.shadow_color = (149, 165, 166, 40)  # Subtle shadow with alpha
        
        # Try to load fonts with improved hierarchy
        self.title_font = self._load_font(size=26, bold=True)  # Slightly larger
        self.heading_font = self._load_font(size=18, bold=True)  # More prominent
        self.body_font = self._load_font(size=13)  # Slightly larger for readability
        self.small_font = self._load_font(size=11)
    
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
    
    def _create_rounded_rectangle_mask(self, size: Tuple[int, int], radius: int) -> Image.Image:
        """Create a rounded rectangle mask."""
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        
        # Draw rounded rectangle by drawing four rounded corners and connecting rectangles
        x, y = size
        draw.rounded_rectangle([0, 0, x, y], radius=radius, fill=255)
        
        return mask
    
    def _create_rounded_rectangle(self, draw: ImageDraw.Draw, bounds: list, radius: int, 
                                fill=None, outline=None, width=1):
        """Draw a rounded rectangle."""
        draw.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=width)
    
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
        # Create base canvas with padding for shadow effect
        shadow_offset = 8
        canvas_width = self.card_width + shadow_offset * 2
        canvas_height = self.card_height + shadow_offset * 2
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))
        
        # Create the main card with rounded corners
        card = Image.new('RGBA', (self.card_width, self.card_height), self.card_bg_color + (255,))
        card_draw = ImageDraw.Draw(card)
        
        # Add subtle shadow effect
        shadow = Image.new('RGBA', (self.card_width, self.card_height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        self._create_rounded_rectangle(shadow_draw, [0, 0, self.card_width, self.card_height], 
                                     self.corner_radius, fill=self.shadow_color)
        
        # Create card background with rounded corners
        self._create_rounded_rectangle(card_draw, [0, 0, self.card_width, self.card_height], 
                                     self.corner_radius, fill=self.card_bg_color)
        
        # Create title bar with rounded top corners
        title_height = 70  # Slightly taller for better proportions
        title_rect = [0, 0, self.card_width, title_height]
        self._create_rounded_rectangle(card_draw, title_rect, self.corner_radius, 
                                     fill=self.title_bg_color)
        
        # Fix the bottom corners of title bar to be square
        card_draw.rectangle([0, title_height - self.corner_radius, self.card_width, title_height], 
                           fill=self.title_bg_color)
        
        # Add title text with better positioning
        title = profile_data.get('title', 'Professional Profile')
        title_bbox = card_draw.textbbox((0, 0), title, font=self.title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.card_width - title_width) // 2
        title_y = (title_height - (title_bbox[3] - title_bbox[1])) // 2
        card_draw.text((title_x, title_y), title, fill=self.title_text_color, font=self.title_font)
        
        # Load and process profile image with rounded corners
        try:
            profile_img = Image.open(image_path)
            profile_img = self._resize_image(profile_img, self.headshot_size)
            
            # Create rounded mask for profile image
            mask = self._create_rounded_rectangle_mask(self.headshot_size, 20)  # Rounded profile image
            profile_img.putalpha(mask)
            
            # Position profile image with better spacing
            img_x = self.margin
            img_y = title_height + self.margin
            
            # Create a white background circle for the profile image
            circle_size = (self.headshot_size[0] + 8, self.headshot_size[1] + 8)
            circle_bg = Image.new('RGBA', circle_size, (255, 255, 255, 255))
            circle_draw = ImageDraw.Draw(circle_bg)
            self._create_rounded_rectangle(circle_draw, [0, 0, circle_size[0], circle_size[1]], 
                                         25, fill=(255, 255, 255), outline=self.border_color, width=2)
            
            # Paste the background and then the profile image
            card.paste(circle_bg, (img_x - 4, img_y - 4), circle_bg)
            card.paste(profile_img, (img_x, img_y), profile_img)
            
        except Exception as e:
            print(f"Warning: Could not load image {image_path}: {e}")
            # Draw modern placeholder
            img_x = self.margin
            img_y = title_height + self.margin
            self._create_rounded_rectangle(card_draw, 
                                         [img_x, img_y, img_x + self.headshot_size[0], 
                                          img_y + self.headshot_size[1]], 
                                         20, fill=self.border_color, outline=self.accent_color, width=2)
            
            # Add placeholder text
            placeholder_text = "No Image"
            text_bbox = card_draw.textbbox((0, 0), placeholder_text, font=self.body_font)
            text_x = img_x + (self.headshot_size[0] - (text_bbox[2] - text_bbox[0])) // 2
            text_y = img_y + (self.headshot_size[1] - (text_bbox[3] - text_bbox[1])) // 2
            card_draw.text((text_x, text_y), placeholder_text, fill=self.text_color, font=self.body_font)
        
        # Calculate text area with improved spacing
        text_x = img_x + self.headshot_size[0] + self.margin
        text_y = title_height + self.margin
        text_width = self.card_width - text_x - self.margin
        
        # Add summary section with modern styling
        summary_bg_y = text_y - 10
        summary_bg_height = 160  # Increased height
        self._create_rounded_rectangle(card_draw, 
                                     [text_x - 15, summary_bg_y, self.card_width - self.margin, 
                                      summary_bg_y + summary_bg_height], 
                                     12, fill=self.section_bg_color, outline=self.border_color, width=1)
        
        # Add a colored accent bar on the left of the summary
        accent_width = 4
        card_draw.rectangle([text_x - 15, summary_bg_y + 5, text_x - 15 + accent_width, 
                           summary_bg_y + summary_bg_height - 5], 
                          fill=self.accent_color)
        
        self._draw_text_section(card_draw, "AI Summary", summary_text, 
                              text_x, text_y + 5, text_width - 20)
        
        # Add additional sections with improved styling
        current_y = text_y + 180  # Adjusted for new summary height
        
        # Add key sections from profile data
        sections_to_show = ['about', 'key_competencies', 'current_aspirations']
        for section_key in sections_to_show:
            if section_key in profile_data and current_y < self.card_height - 100:
                section_title = section_key.replace('_', ' ').title()
                section_content = profile_data[section_key]
                
                # Truncate content if too long
                if len(section_content) > 200:
                    section_content = section_content[:200] + "..."
                
                # Create section background
                section_height = 80  # Fixed height for consistency
                section_bg_y = current_y - 10
                self._create_rounded_rectangle(card_draw, 
                                             [text_x - 15, section_bg_y, self.card_width - self.margin, 
                                              section_bg_y + section_height], 
                                             8, fill=self.section_bg_color, outline=self.border_color, width=1)
                
                section_drawn_height = self._draw_text_section(
                    card_draw, section_title, section_content,
                    text_x, current_y, text_width - 20, max_lines=3
                )
                current_y += section_height + self.section_spacing
        
        # Composite the shadow and card on canvas
        canvas.paste(shadow, (shadow_offset + 2, shadow_offset + 2), shadow)
        canvas.paste(card, (shadow_offset, shadow_offset), card)
        
        # Convert back to RGB for final output
        final_card = Image.new('RGB', (canvas_width, canvas_height), self.bg_color)
        final_card.paste(canvas, (0, 0), canvas)
        
        return final_card
    
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
        
        # Draw title with improved styling
        draw.text((x, current_y), title, fill=self.accent_color, font=self.heading_font)
        current_y += 30  # More space after title
        
        # Draw content with better line spacing
        # Handle bullet points
        if '•' in content:
            lines = content.split('\n')
        else:
            # Wrap text with better character calculation
            chars_per_line = width // 9  # More accurate for modern fonts
            lines = textwrap.wrap(content, width=chars_per_line)
        
        # Limit lines if specified
        if max_lines:
            lines = lines[:max_lines]
        
        for line in lines:
            if current_y > self.card_height - 50:  # Better boundary check
                break
            # Clean up bullet points for better appearance
            if line.strip().startswith('•'):
                line = '  ' + line.strip()  # Add indentation
            draw.text((x, current_y), line, fill=self.text_color, font=self.body_font)
            current_y += 22  # Improved line spacing
        
        return current_y - y
    
    def save_card(self, card: Image.Image, output_path: str):
        """Save the card to a file."""
        card.save(output_path, 'PNG', quality=95)
        print(f"Card saved to: {output_path}")
    
    def get_card_info(self) -> Dict[str, Any]:
        """Get information about card dimensions and settings."""
        shadow_offset = 8
        return {
            "card_size": (self.card_width + shadow_offset * 2, self.card_height + shadow_offset * 2),
            "inner_card_size": (self.card_width, self.card_height),
            "headshot_size": self.headshot_size,
            "colors": {
                "background": self.bg_color,
                "card_background": self.card_bg_color,
                "title_background": self.title_bg_color,
                "text": self.text_color,
                "title_text": self.title_text_color,
                "accent": self.accent_color
            }
        }