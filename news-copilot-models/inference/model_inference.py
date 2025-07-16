"""
Transformer Model Inference and Generation Utilities
"""

import os
import json
import torch
import torch.nn.functional as F
from typing import List, Optional, Dict, Any, Union, Tuple
import time
import logging

from models.transformer_model import TransformerConfig, TransformerForCausalLM
from models.custom_tokenizer import CustomTokenizer

logger = logging.getLogger(__name__)


class TransformerGenerator:
    """High-level interface for text generation with Transformer model"""
    
    def __init__(
        self,
        model_path: str,
        tokenizer_path: Optional[str] = None,
        device: str = "auto",
        torch_dtype: torch.dtype = torch.bfloat16,
        load_in_8bit: bool = False,
        load_in_4bit: bool = False,
    ):
        self.device = self._get_device(device)
        self.torch_dtype = torch_dtype
        
        # Load tokenizer
        if tokenizer_path is None:
            tokenizer_path = model_path
        
        logger.info(f"Loading tokenizer from {tokenizer_path}")
        self.tokenizer = CustomTokenizer.from_pretrained(tokenizer_path)
        
        # Load model
        logger.info(f"Loading model from {model_path}")
        self.model = self._load_model(model_path)
        
        logger.info(f"Model loaded successfully on {self.device}")
    
    def _get_device(self, device: str) -> torch.device:
        """Determine the appropriate device"""
        if device == "auto":
            if torch.cuda.is_available():
                return torch.device("cuda")
            else:
                return torch.device("cpu")
        return torch.device(device)
    
    def _load_model(self, model_path: str) -> TransformerForCausalLM:
        """Load the Transformer model"""
        # Load config
        config_path = os.path.join(model_path, "config.json")
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        
        config = TransformerConfig(**config_dict)
        model = TransformerForCausalLM(config)
        
        # Load weights
        weights_path = os.path.join(model_path, "pytorch_model.bin")
        state_dict = torch.load(weights_path, map_location=self.device)
        model.load_state_dict(state_dict)
        
        model = model.to(self.device, dtype=self.torch_dtype)
        model.eval()
        
        return model
    
    @torch.no_grad()
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 100,
        temperature: float = 0.7,
        top_k: int = 50,
        top_p: float = 0.9,
        do_sample: bool = True,
        repetition_penalty: float = 1.1,
        no_repeat_ngram_size: int = 3,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[int] = None,
        stop_strings: Optional[List[str]] = None,
        return_full_text: bool = False,
    ) -> str:
        """Generate text from a prompt"""
        
        # Tokenize input
        input_ids = self.tokenizer.encode(prompt, add_special_tokens=True)
        input_ids = torch.tensor([input_ids], device=self.device)
        input_length = input_ids.shape[1]
        
        # Set default values
        if pad_token_id is None:
            pad_token_id = self.tokenizer.eos_token_id
        if eos_token_id is None:
            eos_token_id = self.tokenizer.eos_token_id
        
        # Generate
        generated_ids = self._generate_tokens(
            input_ids=input_ids,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            do_sample=do_sample,
            repetition_penalty=repetition_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            pad_token_id=pad_token_id,
            eos_token_id=eos_token_id,
        )
        
        # Decode generated text
        if return_full_text:
            generated_text = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        else:
            new_tokens = generated_ids[0][input_length:]
            generated_text = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        
        # Apply stop strings
        if stop_strings:
            for stop_string in stop_strings:
                if stop_string in generated_text:
                    generated_text = generated_text.split(stop_string)[0]
        
        return generated_text.strip()
    
    def _generate_tokens(
        self,
        input_ids: torch.Tensor,
        max_new_tokens: int,
        temperature: float,
        top_k: int,
        top_p: float,
        do_sample: bool,
        repetition_penalty: float,
        no_repeat_ngram_size: int,
        pad_token_id: int,
        eos_token_id: int,
    ) -> torch.Tensor:
        """Generate tokens using the model"""
        
        batch_size = input_ids.shape[0]
        generated = input_ids
        
        # Keep track of finished sequences
        finished = torch.zeros(batch_size, dtype=torch.bool, device=self.device)
        
        for _ in range(max_new_tokens):
            # Forward pass
            outputs = self.model(input_ids=generated, use_cache=False)
            logits = outputs["logits"][:, -1, :]  # Get logits for last token
            
            # Apply repetition penalty
            if repetition_penalty != 1.0:
                logits = self._apply_repetition_penalty(
                    logits, generated, repetition_penalty, no_repeat_ngram_size
                )
            
            # Apply temperature
            if temperature != 1.0:
                logits = logits / temperature
            
            # Sample next token
            if do_sample:
                # Apply top-k filtering
                if top_k > 0:
                    logits = self._top_k_filtering(logits, top_k)
                
                # Apply top-p (nucleus) filtering
                if top_p < 1.0:
                    logits = self._top_p_filtering(logits, top_p)
                
                # Sample from the filtered distribution
                probs = F.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
            else:
                # Greedy sampling
                next_token = torch.argmax(logits, dim=-1, keepdim=True)
            
            # Add generated token
            generated = torch.cat([generated, next_token], dim=1)
            
            # Check for end of sequence
            finished = finished | (next_token.squeeze() == eos_token_id)
            if finished.all():
                break
        
        return generated
    
    def _apply_repetition_penalty(
        self,
        logits: torch.Tensor,
        input_ids: torch.Tensor,
        penalty: float,
        no_repeat_ngram_size: int,
    ) -> torch.Tensor:
        """Apply repetition penalty to logits"""
        if penalty == 1.0:
            return logits
        
        batch_size, vocab_size = logits.shape
        
        for batch_idx in range(batch_size):
            for token_id in set(input_ids[batch_idx].tolist()):
                # Apply penalty to repeated tokens
                if logits[batch_idx, token_id] < 0:
                    logits[batch_idx, token_id] *= penalty
                else:
                    logits[batch_idx, token_id] /= penalty
        
        # Prevent n-gram repetition
        if no_repeat_ngram_size > 0:
            for batch_idx in range(batch_size):
                # Get the last (no_repeat_ngram_size - 1) tokens
                if input_ids.shape[1] >= no_repeat_ngram_size:
                    ngram = input_ids[batch_idx, -(no_repeat_ngram_size-1):].tolist()
                    
                    # Find all n-grams in the input that start with this prefix
                    for i in range(input_ids.shape[1] - no_repeat_ngram_size + 1):
                        if input_ids[batch_idx, i:i+no_repeat_ngram_size-1].tolist() == ngram:
                            banned_token = input_ids[batch_idx, i+no_repeat_ngram_size-1].item()
                            logits[batch_idx, banned_token] = float('-inf')
        
        return logits
    
    def _top_k_filtering(self, logits: torch.Tensor, top_k: int) -> torch.Tensor:
        """Apply top-k filtering to logits"""
        if top_k <= 0:
            return logits
        
        top_k = min(top_k, logits.size(-1))
        # Get top-k values and indices
        values, indices = torch.topk(logits, top_k, dim=-1)
        
        # Create a mask for top-k tokens
        min_values = values[:, -1:].expand_as(logits)
        logits = torch.where(logits < min_values, torch.full_like(logits, float('-inf')), logits)
        
        return logits
    
    def _top_p_filtering(self, logits: torch.Tensor, top_p: float) -> torch.Tensor:
        """Apply top-p (nucleus) filtering to logits"""
        if top_p >= 1.0:
            return logits
        
        # Sort logits in descending order
        sorted_logits, sorted_indices = torch.sort(logits, descending=True, dim=-1)
        
        # Calculate cumulative probabilities
        cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
        
        # Create mask for tokens to keep
        sorted_indices_to_remove = cumulative_probs > top_p
        # Keep at least one token
        sorted_indices_to_remove[:, 1:] = sorted_indices_to_remove[:, :-1].clone()
        sorted_indices_to_remove[:, 0] = False
        
        # Apply mask to original logits
        indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_indices, sorted_indices_to_remove)
        logits = logits.masked_fill(indices_to_remove, float('-inf'))
        
        return logits
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 200,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate response in chat format"""
        
        # Format messages into a single prompt
        prompt = self._format_chat_prompt(messages)
        
        # Generate response
        response = self.generate(
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            stop_strings=["\n\nUser:", "\n\nAssistant:", "<|im_end|>"],
            **kwargs
        )
        
        return response
    
    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format chat messages into a prompt"""
        prompt = ""
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"
        
        prompt += "Assistant:"
        return prompt
    
    def batch_generate(
        self,
        prompts: List[str],
        max_new_tokens: int = 100,
        batch_size: int = 4,
        **kwargs
    ) -> List[str]:
        """Generate text for multiple prompts"""
        results = []
        
        for i in range(0, len(prompts), batch_size):
            batch_prompts = prompts[i:i+batch_size]
            batch_results = []
            
            for prompt in batch_prompts:
                result = self.generate(
                    prompt=prompt,
                    max_new_tokens=max_new_tokens,
                    **kwargs
                )
                batch_results.append(result)
            
            results.extend(batch_results)
        
        return results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        config = self.model.config
        
        # Calculate approximate model size
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        return {
            "vocab_size": config.vocab_size,
            "hidden_size": config.hidden_size,
            "num_layers": config.num_hidden_layers,
            "num_attention_heads": config.num_attention_heads,
            "num_key_value_heads": config.num_key_value_heads,
            "max_position_embeddings": config.max_position_embeddings,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "device": str(self.device),
            "dtype": str(self.torch_dtype),
        }


class TransformerChatBot:
    """Interactive chatbot using Transformer model"""
    
    def __init__(self, generator: TransformerGenerator, system_prompt: Optional[str] = None):
        self.generator = generator
        self.conversation_history = []
        
        if system_prompt:
            self.conversation_history.append({
                "role": "system",
                "content": system_prompt
            })
    
    def chat(self, user_input: str, **kwargs) -> str:
        """Have a conversation with the model"""
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Generate response
        response = self.generator.chat(
            messages=self.conversation_history,
            **kwargs
        )
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def clear_history(self):
        """Clear conversation history (except system prompt)"""
        system_messages = [msg for msg in self.conversation_history if msg["role"] == "system"]
        self.conversation_history = system_messages
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()


def load_transformer_model(
    model_path: str,
    tokenizer_path: Optional[str] = None,
    device: str = "auto",
    **kwargs
) -> TransformerGenerator:
    """Convenience function to load a Transformer model"""
    return TransformerGenerator(
        model_path=model_path,
        tokenizer_path=tokenizer_path,
        device=device,
        **kwargs
    )


def create_model_chatbot(
    model_path: str,
    system_prompt: Optional[str] = None,
    **kwargs
) -> TransformerChatBot:
    """Convenience function to create a chatbot"""
    generator = load_transformer_model(model_path, **kwargs)
    return TransformerChatBot(generator, system_prompt)


# Example usage and testing functions

def benchmark_generation(generator: TransformerGenerator, num_tests: int = 5) -> Dict[str, float]:
    """Benchmark generation speed"""
    test_prompt = "The future of artificial intelligence is"
    times = []
    
    for _ in range(num_tests):
        start_time = time.time()
        _ = generator.generate(test_prompt, max_new_tokens=100)
        end_time = time.time()
        times.append(end_time - start_time)
    
    return {
        "average_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
        "tokens_per_second": 100 / (sum(times) / len(times))
    }


def interactive_chat(model_path: str, system_prompt: Optional[str] = None):
    """Start an interactive chat session"""
    print("Loading Transformer model...")
    chatbot = create_model_chatbot(model_path, system_prompt)
    
    print("Model loaded! Type 'quit' to exit, 'clear' to clear history.")
    print("=" * 50)
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'clear':
            chatbot.clear_history()
            print("History cleared!")
            continue
        elif not user_input:
            continue
        
        try:
            response = chatbot.chat(user_input)
            print(f"Assistant: {response}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    # Example usage
    model_path = "./checkpoints/final_model"
    
    if os.path.exists(model_path):
        interactive_chat(
            model_path,
            system_prompt="You are a helpful AI assistant specialized in news and current events."
        )
    else:
        print(f"Model not found at {model_path}. Please train a model first.")
