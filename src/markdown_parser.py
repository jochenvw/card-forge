"""
Markdown parser module for CardForge.
Handles parsing and extracting content from markdown files.
"""

import markdown
from typing import Dict, Any
import re


class MarkdownParser:
    """Parses markdown files and extracts structured content."""
    
    def __init__(self):
        self.md = markdown.Markdown(extensions=['meta'])
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a markdown file and extract structured content.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            Dictionary containing parsed content
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> Dict[str, Any]:
        """
        Parse markdown content and extract structured data.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Dictionary with parsed sections
        """
        html = self.md.convert(content)
        
        # Extract sections using regex patterns
        sections = {}
        
        # Extract title (first h1 or h2)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            sections['title'] = title_match.group(1).strip()
        else:
            sections['title'] = "Profile"
        
        # Split content by ## headers and process each section
        # Split on lines that start with ##
        parts = re.split(r'^##\s+', content, flags=re.MULTILINE)
        
        # First part contains title and any content before first ##
        # Skip it and process the rest
        for part in parts[1:]:
            lines = part.split('\n')
            if lines:
                section_name = lines[0].strip().lower().replace(' ', '_')
                section_content = '\n'.join(lines[1:]).strip()
                if section_content:
                    sections[section_name] = section_content
        
        # If no sections found, use the entire content
        if len(sections) == 1:  # Only title
            sections['content'] = content
        
        return sections
    
    def extract_key_points(self, sections: Dict[str, Any]) -> str:
        """
        Extract key points from parsed sections for LLM processing.
        
        Args:
            sections: Parsed markdown sections
            
        Returns:
            Formatted text for LLM input
        """
        key_content = []
        
        # Add title
        if 'title' in sections:
            key_content.append(f"Profile: {sections['title']}")
        
        # Add key sections in order of importance
        priority_sections = [
            'key_competencies', 'competencies', 'skills',
            'current_aspirations', 'aspirations', 'goals',
            'about', 'summary', 'overview',
            'recent_achievements', 'achievements', 'accomplishments'
        ]
        
        for section_key in priority_sections:
            if section_key in sections:
                content = sections[section_key]
                # Clean up markdown formatting
                content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)  # Remove bold
                content = re.sub(r'\*(.+?)\*', r'\1', content)      # Remove italic
                content = re.sub(r'^- ', '', content, flags=re.MULTILINE)  # Clean bullets
                key_content.append(f"{section_key.replace('_', ' ').title()}:\n{content}")
        
        return "\n\n".join(key_content)