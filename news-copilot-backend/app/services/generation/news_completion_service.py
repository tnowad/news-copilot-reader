"""
News Completion Service
Integrates the custom transformer model for intelligent news article completion
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)


class NewsCompletionService:
    """Service for generating news article completions using the custom transformer"""
    
    def __init__(self):
        self.model_loaded = False
        self.generator = None
        self.fallback_mode = True
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the transformer model"""
        try:
            # Add models path
            models_path = os.path.join(os.path.dirname(__file__), '../../../../news-copilot-models')
            if os.path.exists(models_path):
                sys.path.insert(0, models_path)
                
                from inference.model_inference import ModelGenerator
                
                # Try to load the model
                model_path = os.path.join(models_path, 'checkpoints', 'final_model')
                if os.path.exists(model_path):
                    self.generator = ModelGenerator(model_path)
                    self.model_loaded = True
                    self.fallback_mode = False
                    logger.info("Successfully loaded transformer model")
                else:
                    logger.warning(f"Model path {model_path} not found, using fallback")
            else:
                logger.warning("Models directory not found, using fallback")
                
        except Exception as e:
            logger.error(f"Failed to initialize transformer model: {e}")
            self.fallback_mode = True
    
    def complete_article(self, 
                        content: str,
                        max_tokens: int = 100,
                        temperature: float = 0.7,
                        context: str = "news") -> Dict:
        """
        Complete a news article with intelligent context awareness
        
        Args:
            content: Partial article content
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            context: Article context (news, sports, tech, etc.)
            
        Returns:
            Dict with completion results
        """
        try:
            if self.model_loaded and self.generator:
                return self._transformer_completion(content, max_tokens, temperature, context)
            else:
                return self._fallback_completion(content, max_tokens, context)
                
        except Exception as e:
            logger.error(f"Article completion error: {e}")
            return self._fallback_completion(content, max_tokens, context)
    
    def _transformer_completion(self, content: str, max_tokens: int, temperature: float, context: str) -> Dict:
        """Generate completion using the transformer model"""
        try:
            # Optimize parameters based on context
            context_params = self._get_context_parameters(context)
            
            result = self.generator.generate(
                prompt=content,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=context_params['top_p'],
                top_k=context_params['top_k'],
                do_sample=True
            )
            
            return {
                "success": True,
                "completed_text": result,
                "original_length": len(content),
                "generated_length": len(result) - len(content),
                "method": "transformer",
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Transformer completion failed: {e}")
            return self._fallback_completion(content, max_tokens, context)
    
    def _fallback_completion(self, content: str, max_tokens: int, context: str) -> Dict:
        """Fallback completion using rule-based generation"""
        
        context_continuations = {
            "news": [
                " according to recent reports from local authorities.",
                " as confirmed by official sources this morning.",
                " with developments continuing to unfold across the region.",
                " prompting immediate response from emergency services.",
                " affecting thousands of residents in the surrounding area."
            ],
            "sports": [
                " as teams prepare for the upcoming championship rounds.",
                " with players demonstrating exceptional skill and determination.",
                " marking another milestone in this competitive season.",
                " drawing enthusiastic support from fans worldwide.",
                " setting new records in professional athletics."
            ],
            "technology": [
                " representing a significant breakthrough in artificial intelligence.",
                " with implications for the future of digital innovation.",
                " as researchers continue advancing computational capabilities.",
                " potentially transforming how industries operate globally.",
                " demonstrating the rapid pace of technological evolution."
            ],
            "politics": [
                " as lawmakers debate the proposed legislation in congress.",
                " with bipartisan support emerging for key initiatives.",
                " following extensive consultation with community leaders.",
                " amid ongoing discussions about policy implementation.",
                " reflecting changing priorities in government strategy."
            ],
            "business": [
                " as market analysts project continued growth trends.",
                " with investors showing renewed confidence in the sector.",
                " following successful quarterly earnings reports.",
                " indicating positive economic indicators for the region.",
                " as companies adapt to evolving consumer demands."
            ],
            "health": [
                " according to leading medical researchers and practitioners.",
                " as healthcare professionals recommend updated protocols.",
                " with clinical trials showing promising preliminary results.",
                " supporting evidence-based approaches to patient care.",
                " advancing our understanding of preventive medicine."
            ]
        }
        
        # Select appropriate continuation
        continuations = context_continuations.get(context, context_continuations["news"])
        import random
        selected_continuation = random.choice(continuations)
        
        # Generate completion based on content length and context
        if len(content.split()) < 10:
            # Short content - add substantial completion
            completion = content + selected_continuation + " The situation continues to develop as officials monitor ongoing changes and provide regular updates to keep the public informed about important developments."
        else:
            # Longer content - add shorter completion
            completion = content + selected_continuation
        
        # Trim to approximate token count
        words = completion.split()
        if len(words) > len(content.split()) + max_tokens:
            completion = " ".join(words[:len(content.split()) + max_tokens])
        
        return {
            "success": True,
            "completed_text": completion,
            "original_length": len(content),
            "generated_length": len(completion) - len(content),
            "method": "fallback",
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_context_parameters(self, context: str) -> Dict:
        """Get optimized parameters for different contexts"""
        context_params = {
            "news": {"top_p": 0.85, "top_k": 30},
            "sports": {"top_p": 0.9, "top_k": 35},
            "technology": {"top_p": 0.88, "top_k": 40},
            "politics": {"top_p": 0.8, "top_k": 25},
            "business": {"top_p": 0.85, "top_k": 30},
            "health": {"top_p": 0.82, "top_k": 28},
            "entertainment": {"top_p": 0.92, "top_k": 45}
        }
        
        return context_params.get(context, {"top_p": 0.85, "top_k": 30})
    
    def generate_headline(self, content: str, style: str = "standard") -> str:
        """Generate a headline for the given content"""
        try:
            # Extract key information for headline
            words = content.split()
            if len(words) < 5:
                return "Breaking News: Latest Updates"
            
            # Simple headline generation based on content
            first_sentence = content.split('.')[0]
            if len(first_sentence) > 80:
                first_sentence = first_sentence[:80] + "..."
            
            style_prefixes = {
                "breaking": "BREAKING: ",
                "update": "UPDATE: ",
                "analysis": "ANALYSIS: ",
                "exclusive": "EXCLUSIVE: ",
                "standard": ""
            }
            
            prefix = style_prefixes.get(style, "")
            return prefix + first_sentence
            
        except Exception as e:
            logger.error(f"Headline generation error: {e}")
            return "Latest News Update"
    
    def get_service_status(self) -> Dict:
        """Get current service status"""
        return {
            "model_loaded": self.model_loaded,
            "fallback_mode": self.fallback_mode,
            "service_healthy": True,
            "timestamp": datetime.now().isoformat()
        }


# Global service instance
news_completion_service = NewsCompletionService()
