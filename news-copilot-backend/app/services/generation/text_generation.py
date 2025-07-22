import sys
import os
import torch
from typing import Dict, Any, Optional

# Add the models directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../news-copilot-models'))

try:
    from models.transformer_model import TransformerForCausalLM, TransformerConfig
    from models.custom_tokenizer import CustomTokenizer
    from inference.model_inference import ModelGenerator
    
    class NewsTransformerGenerator:
        """News completion generator using the custom transformer model"""
        
        def __init__(self, model_path: str = None):
            self.model_path = model_path or "./news-copilot-models/checkpoints/final_model"
            self.generator = None
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self._load_model()
        
        def _load_model(self):
            """Load the transformer model and tokenizer"""
            try:
                self.generator = ModelGenerator(self.model_path)
                print(f"Successfully loaded transformer model from {self.model_path}")
            except Exception as e:
                print(f"Failed to load transformer model: {e}")
                print("Using fallback text completion...")
                self.generator = None
        
        def generate_text(self, 
                         prompt: str,
                         max_new_tokens: int = 50,
                         temperature: float = 0.7,
                         top_p: float = 0.9,
                         top_k: int = 20,
                         do_sample: bool = True) -> str:
            """Generate text completion for news articles"""
            
            if self.generator is None:
                # Fallback for when model is not available
                return self._fallback_generation(prompt, max_new_tokens)
            
            try:
                # Use the custom transformer for generation
                result = self.generator.generate(
                    prompt=prompt,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    do_sample=do_sample,
                    pad_token_id=self.generator.tokenizer.pad_token_id
                )
                
                return result
                
            except Exception as e:
                print(f"Generation error: {e}")
                return self._fallback_generation(prompt, max_new_tokens)
        
        def _fallback_generation(self, prompt: str, max_length: int) -> str:
            """Fallback generation when model is not available"""
            fallback_completions = {
                "breaking": " news just in: significant developments reported across multiple sectors...",
                "technology": " advances continue to reshape industries with artificial intelligence leading innovation...",
                "sports": " update: teams prepare for upcoming matches with renewed strategies and player rotations...",
                "weather": " forecast indicates changing conditions with temperatures varying across regions...",
                "economy": " indicators show mixed signals as markets respond to recent policy changes...",
                "health": " officials announce new guidelines following recent research findings...",
                "politics": " leaders address key issues in ongoing discussions about policy reforms...",
                "environment": " scientists report new findings about climate patterns and conservation efforts...",
                "education": " institutions implement innovative approaches to enhance learning outcomes...",
                "entertainment": " industry figures announce exciting projects and collaborations..."
            }
            
            prompt_lower = prompt.lower()
            for key, completion in fallback_completions.items():
                if key in prompt_lower:
                    return prompt + completion[:max_length]
            
            return prompt + " continues to develop as more information becomes available..."

    # Initialize the global generator
    news_generator = NewsTransformerGenerator()
    
    def text_generation_pipeline(prompt: str, 
                                max_length: int = 100,
                                temperature: float = 0.7,
                                top_k: int = 20,
                                top_p: float = 0.9) -> list:
        """
        Compatible interface with the old pipeline for backward compatibility
        """
        generated_text = news_generator.generate_text(
            prompt=prompt,
            max_new_tokens=max_length,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p
        )
        
        return [{"generated_text": generated_text}]

except ImportError as e:
    print(f"Failed to import transformer components: {e}")
    print("Using fallback text generation...")
    
    def text_generation_pipeline(prompt: str,
                                max_length: int = 100,
                                temperature: float = 0.7,
                                top_k: int = 20,
                                top_p: float = 0.9) -> list:
        """Fallback text generation when transformer is not available"""
        
        # Simple rule-based completions for news
        completions = {
            "breaking": f"{prompt} news alerts indicate significant developments across multiple regions with authorities responding to emerging situations...",
            "technology": f"{prompt} innovations continue advancing with artificial intelligence and machine learning driving unprecedented changes in various industries...",
            "sports": f"{prompt} updates reveal competitive matches and player performances as teams prepare for upcoming tournaments and league competitions...",
            "weather": f"{prompt} patterns show changing conditions with meteorologists tracking systems that may impact regional forecasting and planning...",
            "economy": f"{prompt} indicators demonstrate market fluctuations as analysts monitor trends affecting global trade and financial stability...",
            "health": f"{prompt} research reveals important findings that could influence medical practices and public health policy recommendations...",
            "politics": f"{prompt} developments show leaders addressing critical issues through diplomatic channels and legislative processes...",
            "environment": f"{prompt} studies highlight conservation efforts and climate research that inform environmental protection strategies...",
            "education": f"{prompt} initiatives focus on improving learning outcomes through innovative teaching methods and educational technology integration...",
            "entertainment": f"{prompt} industry news features upcoming releases and creative collaborations among artists and production companies..."
        }
        
        prompt_lower = prompt.lower()
        for key, completion in completions.items():
            if key in prompt_lower:
                return [{"generated_text": completion[:len(prompt) + max_length]}]
        
        # Default completion
        default_completion = f"{prompt} story continues to develop as journalists gather more information and officials prepare statements for the public..."
        return [{"generated_text": default_completion[:len(prompt) + max_length]}]
