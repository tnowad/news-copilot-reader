"""
Training configuration for Transformer model
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass
class TrainingConfig:
    """Configuration for training Transformer model"""
    
    # Model architecture
    vocab_size: int = 32000
    hidden_size: int = 4096
    intermediate_size: int = 14336
    num_hidden_layers: int = 32
    num_attention_heads: int = 32
    num_key_value_heads: int = 8  # For Grouped Query Attention
    head_dim: Optional[int] = None
    max_position_embeddings: int = 32768
    rms_norm_eps: float = 1e-6
    rope_theta: float = 10000.0
    sliding_window: Optional[int] = 4096
    attention_dropout: float = 0.0
    hidden_act: str = "silu"
    initializer_range: float = 0.02
    
    # Training hyperparameters
    learning_rate: float = 3e-4
    min_learning_rate: float = 3e-5
    weight_decay: float = 0.01
    beta1: float = 0.9
    beta2: float = 0.95
    epsilon: float = 1e-8
    grad_clip: float = 1.0
    
    # Training schedule
    num_epochs: int = 3
    max_steps: int = -1
    warmup_steps: int = 2000
    warmup_ratio: float = 0.03
    lr_scheduler: str = "cosine"  # "cosine", "linear", "constant"
    
    # Batch sizes and data
    batch_size: int = 4
    micro_batch_size: int = 1
    gradient_accumulation_steps: int = 4
    max_seq_len: int = 4096
    data_loader_workers: int = 4
    
    # Mixed precision and optimization
    use_mixed_precision: bool = True
    precision_type: str = "bf16"  # "fp16", "bf16"
    use_gradient_checkpointing: bool = True
    use_flash_attention: bool = True
    
    # Evaluation and logging
    eval_interval: int = 1000
    log_interval: int = 100
    save_interval: int = 1000
    eval_iters: int = 200
    eval_only: bool = False
    always_save_checkpoint: bool = True
    
    # Paths and directories
    out_dir: str = "./checkpoints"
    data_dir: str = "./data"
    init_from: str = "scratch"  # "scratch", "resume", "gpt2*"
    
    # Data settings
    dataset: str = "custom"
    train_data_path: str = "./data/train.txt"
    val_data_path: str = "./data/val.txt"
    
    # Tokenizer settings
    tokenizer_path: Optional[str] = None
    create_tokenizer: bool = True
    tokenizer_vocab_size: int = 32000
    
    # System settings
    device: str = "auto"  # "auto", "cuda", "cpu"
    compile_model: bool = True
    dtype: str = "bfloat16"  # "float32", "bfloat16", "float16"
    
    # Distributed training
    backend: str = "nccl"
    
    # Experiment tracking
    wandb_log: bool = False
    wandb_project: str = "transformer-news-training"
    wandb_run_name: Optional[str] = None
    
    # Model-specific settings
    tie_embeddings: bool = False
    use_cache: bool = True
    
    def __post_init__(self):
        if self.head_dim is None:
            self.head_dim = self.hidden_size // self.num_attention_heads
        
        # Calculate gradient accumulation steps
        if self.gradient_accumulation_steps is None:
            self.gradient_accumulation_steps = self.batch_size // self.micro_batch_size
        
        # Validate configuration
        assert self.hidden_size % self.num_attention_heads == 0
        assert self.num_attention_heads % self.num_key_value_heads == 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "TrainingConfig":
        """Create from dictionary"""
        return cls(**config_dict)


# Predefined configurations for different model sizes

@dataclass
class TransformerTinyConfig(TrainingConfig):
    """Tiny Transformer for testing (similar to GPT-2 small)"""
    hidden_size: int = 768
    intermediate_size: int = 3072
    num_hidden_layers: int = 12
    num_attention_heads: int = 12
    num_key_value_heads: int = 4
    max_position_embeddings: int = 2048
    vocab_size: int = 32000


@dataclass
class TransformerSmallConfig(TrainingConfig):
    """Small Transformer (1B parameters)"""
    hidden_size: int = 2048
    intermediate_size: int = 5632
    num_hidden_layers: int = 24
    num_attention_heads: int = 16
    num_key_value_heads: int = 4
    max_position_embeddings: int = 8192
    vocab_size: int = 32000


@dataclass
class TransformerMediumConfig(TrainingConfig):
    """Medium Transformer (3B parameters)"""
    hidden_size: int = 2560
    intermediate_size: int = 6912
    num_hidden_layers: int = 32
    num_attention_heads: int = 20
    num_key_value_heads: int = 5
    max_position_embeddings: int = 16384
    vocab_size: int = 32000


@dataclass
class TransformerLargeConfig(TrainingConfig):
    """Large Transformer (7B parameters) - Original Transformer-7B size"""
    hidden_size: int = 4096
    intermediate_size: int = 14336
    num_hidden_layers: int = 32
    num_attention_heads: int = 32
    num_key_value_heads: int = 8
    max_position_embeddings: int = 32768
    vocab_size: int = 32000


# Helper function to get config by name
def get_config(config_name: str = "large") -> TrainingConfig:
    """Get predefined configuration by name"""
    configs = {
        "tiny": TransformerTinyConfig(),
        "small": TransformerSmallConfig(),
        "medium": TransformerMediumConfig(),
        "large": TransformerLargeConfig(),
    }
    
    if config_name not in configs:
        raise ValueError(f"Unknown config: {config_name}. Available: {list(configs.keys())}")
    
    return configs[config_name]


# Default configuration
default_config = TransformerLargeConfig()
