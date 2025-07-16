"""
Transformer Model Implementation Package

This package contains a complete from-scratch implementation of the Transformer-7B
architecture for training and inference, specifically designed for the News
Copilot project.

Key Components:
- TransformerForCausalLM: Complete model implementation
- CustomTokenizer: SentencePiece-based tokenizer
- TransformerTrainer: Training pipeline
- TransformerGenerator: Inference utilities

Quick Usage:
    from models.transformer_model import TransformerForCausalLM, TransformerConfig
    from models.custom_tokenizer import CustomTokenizer
    from inference.model_inference import TransformerGenerator
    
    # Create model
    config = TransformerConfig(vocab_size=32000)
    model = TransformerForCausalLM(config)
    
    # Load for inference
    generator = TransformerGenerator("./path/to/model")
    text = generator.generate("Your prompt here")
"""

__version__ = "1.0.0"
__author__ = "News Copilot Team"

# Import key classes for convenience
try:
    from .models.transformer_model import (
        TransformerConfig,
        TransformerForCausalLM,
        TransformerModel,
        TransformerPreTrainedModel
    )
    from .models.custom_tokenizer import (
        CustomTokenizer,
        create_custom_tokenizer_from_texts,
        prepare_training_data
    )
    from .config.training_config import (
        TrainingConfig,
        TransformerTinyConfig,
        TransformerSmallConfig,
        TransformerMediumConfig,
        TransformerLargeConfig,
        get_config
    )
    from .inference.model_inference import (
        TransformerGenerator,
        TransformerChatBot,
        load_transformer_model,
        create_model_chatbot
    )
    
    __all__ = [
        # Model classes
        "TransformerConfig",
        "TransformerForCausalLM", 
        "TransformerModel",
        "TransformerPreTrainedModel",
        
        # Tokenizer classes
        "CustomTokenizer",
        "create_custom_tokenizer_from_texts",
        "prepare_training_data",
        
        # Config classes
        "TrainingConfig",
        "TransformerTinyConfig",
        "TransformerSmallConfig", 
        "TransformerMediumConfig",
        "TransformerLargeConfig",
        "get_config",
        
        # Inference classes
        "TransformerGenerator",
        "TransformerChatBot",
        "load_transformer_model",
        "create_model_chatbot",
    ]
    
except ImportError as e:
    # Handle import errors gracefully during development
    print(f"Warning: Could not import all modules: {e}")
    __all__ = []
