"""
Custom Tokenizer Implementation
"""

import json
import os
import re
from typing import List, Dict, Optional, Union, Tuple
import sentencepiece as spm


class CustomTokenizer:
    """Custom tokenizer using SentencePiece"""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        vocab_size: int = 32000,
        bos_token: str = "<s>",
        eos_token: str = "</s>",
        unk_token: str = "<unk>",
        pad_token: str = "<pad>",
    ):
        self.vocab_size = vocab_size
        self.bos_token = bos_token
        self.eos_token = eos_token
        self.unk_token = unk_token
        self.pad_token = pad_token
        
        # Special token IDs
        self.bos_token_id = 1
        self.eos_token_id = 2
        self.unk_token_id = 0
        self.pad_token_id = None  # Transformer doesn't use padding by default
        
        self.sp_model = None
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
    
    def train(
        self, 
        input_files: List[str], 
        model_prefix: str,
        vocab_size: int = 32000,
        character_coverage: float = 0.9995,
        model_type: str = 'bpe'
    ):
        """Train SentencePiece model"""
        input_argument = ','.join(input_files)
        
        cmd = f"""
        --input={input_argument}
        --model_prefix={model_prefix}
        --vocab_size={vocab_size}
        --character_coverage={character_coverage}
        --model_type={model_type}
        --bos_id={self.bos_token_id}
        --eos_id={self.eos_token_id}
        --unk_id={self.unk_token_id}
        --bos_piece={self.bos_token}
        --eos_piece={self.eos_token}
        --unk_piece={self.unk_token}
        --user_defined_symbols={self.pad_token}
        --byte_fallback=true
        --split_digits=true
        --allow_whitespace_only_pieces=true
        --remove_extra_whitespaces=false
        --normalization_rule_name=identity
        """.replace('\n', ' ').strip()
        
        spm.SentencePieceTrainer.train(cmd)
        self.load_model(f"{model_prefix}.model")
    
    def load_model(self, model_path: str):
        """Load trained SentencePiece model"""
        self.sp_model = spm.SentencePieceProcessor()
        self.sp_model.load(model_path)
        
        # Update vocab size with actual model size
        self.vocab_size = self.sp_model.get_piece_size()
        
        # Find pad token ID if it exists
        if self.pad_token in [self.sp_model.id_to_piece(i) for i in range(self.vocab_size)]:
            self.pad_token_id = self.sp_model.piece_to_id(self.pad_token)
    
    def encode(
        self, 
        text: str, 
        add_special_tokens: bool = True,
        max_length: Optional[int] = None,
        padding: bool = False,
        truncation: bool = False
    ) -> List[int]:
        """Encode text to token IDs"""
        if self.sp_model is None:
            raise ValueError("Model not loaded. Call load_model() or train() first.")
        
        # Encode text
        tokens = self.sp_model.encode(text, out_type=int)
        
        # Add special tokens
        if add_special_tokens:
            tokens = [self.bos_token_id] + tokens + [self.eos_token_id]
        
        # Truncation
        if truncation and max_length:
            if len(tokens) > max_length:
                if add_special_tokens:
                    # Keep BOS and EOS, truncate middle
                    tokens = [tokens[0]] + tokens[1:max_length-1] + [tokens[-1]]
                else:
                    tokens = tokens[:max_length]
        
        # Padding
        if padding and max_length and self.pad_token_id is not None:
            if len(tokens) < max_length:
                tokens = tokens + [self.pad_token_id] * (max_length - len(tokens))
        
        return tokens
    
    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode token IDs to text"""
        if self.sp_model is None:
            raise ValueError("Model not loaded. Call load_model() or train() first.")
        
        # Filter special tokens if requested
        if skip_special_tokens:
            special_ids = {self.bos_token_id, self.eos_token_id, self.unk_token_id}
            if self.pad_token_id is not None:
                special_ids.add(self.pad_token_id)
            token_ids = [tid for tid in token_ids if tid not in special_ids]
        
        return self.sp_model.decode(token_ids)
    
    def batch_encode(
        self,
        texts: List[str],
        add_special_tokens: bool = True,
        max_length: Optional[int] = None,
        padding: bool = True,
        truncation: bool = True,
        return_attention_mask: bool = True
    ) -> Dict[str, List[List[int]]]:
        """Batch encode multiple texts"""
        all_input_ids = []
        all_attention_masks = []
        
        for text in texts:
            input_ids = self.encode(
                text, 
                add_special_tokens=add_special_tokens,
                max_length=max_length,
                padding=False,  # We'll handle padding after
                truncation=truncation
            )
            all_input_ids.append(input_ids)
        
        # Determine max length for padding
        if padding and max_length is None:
            max_length = max(len(ids) for ids in all_input_ids)
        
        # Apply padding and create attention masks
        for i, input_ids in enumerate(all_input_ids):
            attention_mask = [1] * len(input_ids)
            
            if padding and max_length and len(input_ids) < max_length:
                if self.pad_token_id is not None:
                    pad_length = max_length - len(input_ids)
                    input_ids.extend([self.pad_token_id] * pad_length)
                    attention_mask.extend([0] * pad_length)
                else:
                    # If no pad token, use unk token for padding
                    pad_length = max_length - len(input_ids)
                    input_ids.extend([self.unk_token_id] * pad_length)
                    attention_mask.extend([0] * pad_length)
            
            all_input_ids[i] = input_ids
            all_attention_masks.append(attention_mask)
        
        result = {"input_ids": all_input_ids}
        if return_attention_mask:
            result["attention_mask"] = all_attention_masks
        
        return result
    
    def get_vocab_size(self) -> int:
        """Get vocabulary size"""
        return self.vocab_size
    
    def get_vocab(self) -> Dict[str, int]:
        """Get vocabulary as token -> id mapping"""
        if self.sp_model is None:
            return {}
        
        vocab = {}
        for i in range(self.vocab_size):
            piece = self.sp_model.id_to_piece(i)
            vocab[piece] = i
        return vocab
    
    def save_pretrained(self, save_directory: str):
        """Save tokenizer to directory"""
        os.makedirs(save_directory, exist_ok=True)
        
        # Save tokenizer config
        config = {
            "vocab_size": self.vocab_size,
            "bos_token": self.bos_token,
            "eos_token": self.eos_token,
            "unk_token": self.unk_token,
            "pad_token": self.pad_token,
            "bos_token_id": self.bos_token_id,
            "eos_token_id": self.eos_token_id,
            "unk_token_id": self.unk_token_id,
            "pad_token_id": self.pad_token_id,
        }
        
        with open(os.path.join(save_directory, "tokenizer_config.json"), "w") as f:
            json.dump(config, f, indent=2)
        
        # Copy model file if it exists
        if self.sp_model is not None:
            import shutil
            model_path = os.path.join(save_directory, "tokenizer.model")
            # Note: This assumes the model file is accessible
            # In practice, you'd need to save the actual model file
    
    @classmethod
    def from_pretrained(cls, model_path: str) -> "CustomTokenizer":
        """Load tokenizer from directory"""
        config_path = os.path.join(model_path, "tokenizer_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
            
            tokenizer = cls(**config)
            
            # Load model file
            model_file = os.path.join(model_path, "tokenizer.model")
            if os.path.exists(model_file):
                tokenizer.load_model(model_file)
            
            return tokenizer
        else:
            # Try to load just the model file
            model_file = os.path.join(model_path, "tokenizer.model")
            return cls(model_path=model_file)


def prepare_training_data(texts: List[str], output_file: str):
    """Prepare text data for SentencePiece training"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for text in texts:
            # Basic text cleaning
            text = text.strip()
            if text:
                f.write(text + '\n')


def create_custom_tokenizer_from_texts(
    texts: List[str],
    model_name: str = "custom_tokenizer",
    vocab_size: int = 32000,
    save_dir: str = "./tokenizer"
) -> CustomTokenizer:
    """Create and train a tokenizer from scratch"""
    
    # Prepare training data
    training_file = f"{model_name}_training.txt"
    prepare_training_data(texts, training_file)
    
    # Create and train tokenizer
    tokenizer = CustomTokenizer(vocab_size=vocab_size)
    tokenizer.train([training_file], model_name, vocab_size=vocab_size)
    
    # Save tokenizer
    os.makedirs(save_dir, exist_ok=True)
    tokenizer.save_pretrained(save_dir)
    
    # Clean up training file
    if os.path.exists(training_file):
        os.remove(training_file)
    
    return tokenizer
