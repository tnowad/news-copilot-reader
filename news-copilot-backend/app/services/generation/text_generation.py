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
            fallback_phrases = [
                " according to official sources.",
                " as confirmed by recent reports.",
                " with further details expected soon.",
                " marking a notable development in the region.",
                " drawing attention from analysts worldwide.",
                " as stakeholders closely monitor the situation.",
                " prompting discussion among experts in the field.",
                " with implications for future policy decisions.",
                " reflecting broader trends in the industry.",
                " as the situation continues to evolve.",
            ]

            import random
            if len(prompt) > 20:
                return prompt + random.choice(fallback_phrases)
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

    import random

    _FALLBACK_PHRASES = [
        " according to officials familiar with the matter.",
        " as confirmed by multiple sources close to the investigation.",
        " with authorities urging the public to remain patient.",
        " while experts weigh in on the broader implications.",
        " though details remain sparse at this early stage.",
        " and more information is expected in the coming days.",
        " as community leaders call for immediate action.",
        " marking a significant shift in the ongoing discourse.",
        " fueling debate among analysts and policymakers.",
        " with reactions pouring in from across the industry.",
        " as the story continues to capture public attention.",
        " prompting renewed scrutiny of related policies.",
        " echoing concerns raised by advocacy groups.",
        " as stakeholders await further clarification.",
        " triggering a wave of responses on social media.",
        " with updates expected following the next briefing.",
    ]

    _DEFAULT_PREFIXES = [
        "The development follows",
        "This comes as",
        "Reports indicate that",
        "Analysts suggest",
        "Observers noted that",
        "Initial findings show",
        "Authorities stated that",
        "Witnesses reported",
        "Experts believe",
        "Sources claim",
    ]

    def text_generation_pipeline(prompt: str,
                                max_length: int = 100,
                                temperature: float = 0.7,
                                top_k: int = 20,
                                top_p: float = 0.9) -> list:
        """Fallback text generation when transformer is not available"""

        words = prompt.split()
        options = sum(length <= max_length for length in [30, 60, 100])
        choices = []

        for _ in range(min(3, max_length // 30 + 1)):
            prefix = random.choice(_DEFAULT_PREFIXES)
            phrase = random.choice(_FALLBACK_PHRASES)
            choices.append(f"{prefix} {phrase}")

        if len(words) < 10:
            result = f"{prompt}. {''.join(random.sample(choices, min(2, len(choices))))}"
        else:
            result = f"{prompt}{random.choice(_FALLBACK_PHRASES)}"

        return [{"generated_text": result[:len(prompt) + max_length]}]
