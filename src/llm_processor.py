"""
LLM processor module for CardForge.
Handles local LLM inference for text summarization and transformation.
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from typing import Optional, Dict, Any
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProcessor:
    """Handles local LLM inference for text processing."""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """
        Initialize the LLM processor.
        
        Args:
            model_name: Name of the model to use for inference
                       Default is a smaller model for testing. For production,
                       use "mistralai/Mistral-7B-Instruct-v0.1" or similar
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
        logger.info(f"LLM Processor initialized with device: {self.device}")
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load the model and tokenizer."""
        try:
            logger.info(f"Loading model: {self.model_name}")
            
            # For this MVP, we'll use a simpler text generation approach
            # In production, use a proper instruction-following model
            if "DialoGPT" in self.model_name:
                # Lightweight model for testing
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
                
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                
                self.model.to(self.device)
                
            else:
                # For larger models like Mistral
                self.pipeline = pipeline(
                    "text-generation",
                    model=self.model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None,
                )
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Fallback to a simple rule-based approach
            logger.warning("Falling back to rule-based text processing")
            self.model = None
            self.tokenizer = None
            self.pipeline = None
    
    def summarize_profile(self, text: str, max_bullets: int = 4) -> str:
        """
        Summarize profile text into key bullet points.
        
        Args:
            text: Input text to summarize
            max_bullets: Maximum number of bullet points to generate
            
        Returns:
            Summarized text with bullet points
        """
        if self.pipeline:
            return self._summarize_with_pipeline(text, max_bullets)
        elif self.model and self.tokenizer:
            return self._summarize_with_model(text, max_bullets)
        else:
            return self._summarize_rule_based(text, max_bullets)
    
    def _summarize_with_pipeline(self, text: str, max_bullets: int) -> str:
        """Summarize using Hugging Face pipeline."""
        prompt = f"""Summarize this profile in {max_bullets} clear bullet points highlighting the most important skills and aspirations:

{text}

Summary:
•"""
        
        try:
            result = self.pipeline(
                prompt,
                max_new_tokens=200,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.pipeline.tokenizer.eos_token_id
            )
            
            generated_text = result[0]['generated_text']
            # Extract the summary part
            summary_start = generated_text.find("Summary:")
            if summary_start != -1:
                summary = generated_text[summary_start + len("Summary:"):]
                return self._clean_summary(summary)
            
        except Exception as e:
            logger.error(f"Error in pipeline summarization: {e}")
        
        # Fallback to rule-based
        return self._summarize_rule_based(text, max_bullets)
    
    def _summarize_with_model(self, text: str, max_bullets: int) -> str:
        """Summarize using loaded model and tokenizer."""
        prompt = f"Profile summary: {text[:500]}..."  # Truncate for smaller models
        
        try:
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 100,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract the new part
            summary = generated[len(prompt):].strip()
            return self._clean_summary(summary) if summary else self._summarize_rule_based(text, max_bullets)
            
        except Exception as e:
            logger.error(f"Error in model summarization: {e}")
        
        # Fallback to rule-based
        return self._summarize_rule_based(text, max_bullets)
    
    def _summarize_rule_based(self, text: str, max_bullets: int) -> str:
        """Fallback rule-based summarization."""
        logger.info("Using rule-based summarization")
        
        # Extract key phrases and sentences
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Look for bullet points or key information
        bullets = []
        current_section = ""
        
        for line in lines:
            # Check if this is a section header
            if ':' in line and not line.startswith('-') and not line.startswith('*'):
                current_section = line.split(':')[0].strip()
                continue
            
            # Process bullet points
            if line.startswith('-') or line.startswith('*'):
                # Clean and extract key info
                clean_line = line.lstrip('- *').strip()
                # Remove markdown formatting
                clean_line = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_line)  # Remove bold
                clean_line = re.sub(r'\*(.+?)\*', r'\1', clean_line)      # Remove italic
                
                if len(clean_line) > 10:  # Filter out very short lines
                    # Extract key skill/achievement
                    if ':' in clean_line:
                        skill_part = clean_line.split(':')[0].strip()
                        bullets.append(f"• {skill_part}")
                    else:
                        bullets.append(f"• {clean_line}")
        
        # If no bullets found, extract key sentences from text
        if not bullets:
            # Look for key competencies, skills, aspirations
            for line in lines:
                if any(keyword in line.lower() for keyword in ['expert', 'experience', 'proficiency', 'leading', 'building']):
                    clean_line = line.strip().replace('- ', '').replace('* ', '')
                    if len(clean_line) > 10:
                        bullets.append(f"• {clean_line}")
        
        # If still no bullets, fall back to first few meaningful lines
        if not bullets:
            sentences = []
            for line in lines:
                if len(line) > 20 and not line.startswith('#'):
                    sentences.append(line)
            bullets = [f"• {s}" for s in sentences[:max_bullets]]
        
        # Limit to max_bullets and ensure unique
        unique_bullets = []
        seen = set()
        for bullet in bullets:
            if bullet not in seen and len(unique_bullets) < max_bullets:
                unique_bullets.append(bullet)
                seen.add(bullet)
        
        return '\n'.join(unique_bullets)
    
    def _clean_summary(self, summary: str) -> str:
        """Clean up generated summary text."""
        # Remove extra whitespace and format bullets
        lines = [line.strip() for line in summary.split('\n') if line.strip()]
        cleaned = []
        
        for line in lines:
            if line and not line.startswith('•'):
                line = f"• {line}"
            cleaned.append(line)
        
        return '\n'.join(cleaned[:4])  # Limit to 4 bullets
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get information about the device and model."""
        return {
            "device": self.device,
            "model_name": self.model_name,
            "cuda_available": torch.cuda.is_available(),
            "model_loaded": self.model is not None or self.pipeline is not None
        }