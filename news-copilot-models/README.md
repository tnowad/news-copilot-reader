# Advanced Transformer Language Model

A complete from-scratch implementation of a state-of-the-art transformer architecture for training and inference, specifically designed for the News Copilot project.

## Features

- **Advanced Transformer Architecture**: Full implementation including:
  - Grouped Query Attention (GQA)
  - Sliding Window Attention
  - RMSNorm normalization
  - SwiGLU activation function
  - Rotary Position Embeddings (RoPE)
  - SentencePiece tokenization

- **Training Pipeline**: Comprehensive training system with:
  - Mixed precision training (FP16/BF16)
  - Gradient accumulation and checkpointing
  - Distributed training support
  - WandB integration
  - Learning rate scheduling

- **Inference Utilities**: High-level inference API with:
  - Text generation with various sampling strategies
  - Chat interface
  - Batch generation
  - Interactive CLI

## Project Structure

```
news-copilot-models/
├── models/
│   ├── transformer_model.py     # Core transformer architecture
│   └── custom_tokenizer.py      # SentencePiece tokenizer
├── config/
│   ├── model_config.py          # Model configuration
│   └── training_config.py       # Training configurations
├── training/
│   └── train_model.py           # Training pipeline
├── inference/
│   └── model_inference.py       # Inference utilities
├── utils/
│   └── model_utils.py           # Utility scripts
├── data/                        # Training data (to be created)
├── checkpoints/                 # Model checkpoints (to be created)
└── requirements.txt             # Dependencies
```

## Installation

1. Install dependencies:
```bash
cd news-copilot-models
pip install -r requirements.txt
```

2. Additional dependencies for SentencePiece:
```bash
# For Ubuntu/Debian
sudo apt-get install cmake build-essential pkg-config libgoogle-perftools-dev

# Install SentencePiece
pip install sentencepiece
```

## Quick Start

### 1. Create Sample Training Data

```bash
python utils/model_utils.py data --output ./data/sample_news.txt
```

### 2. Train a Small Model (for testing)

```bash
python utils/model_utils.py train \
    --config tiny \
    --data ./data/sample_news.txt \
    --output ./checkpoints \
    --epochs 1 \
    --batch-size 1
```

### 3. Test Inference

```bash
python utils/model_utils.py test ./checkpoints/final_model
```

### 4. Interactive Chat

```bash
python utils/model_utils.py chat ./checkpoints/final_model
```

## Model Configurations

Several pre-configured model sizes are available:

| Config | Parameters | Hidden Size | Layers | Attention Heads | Use Case |
|--------|------------|-------------|--------|-----------------|----------|
| tiny   | ~125M      | 768         | 12     | 12              | Testing, Development |
| small  | ~1B        | 2048        | 24     | 16              | Experiments |
| medium | ~3B        | 2560        | 32     | 20              | Production (small) |
| large  | ~7B        | 4096        | 32     | 32              | Full-scale model |

## Training Your Own Model

### Prepare Your Data

Your training data should be in one of these formats:

1. **Plain text file** (`.txt`): One document per line
2. **JSON file** (`.json`): Array of strings or `{"texts": [...]}`
3. **JSONL file** (`.jsonl`): One JSON object per line with `text` or `content` fields

Example:
```python
# For news articles
articles = [
    "Breaking: New AI breakthrough announced...",
    "Technology companies report strong earnings...",
    "Climate change study reveals..."
]

with open("./data/news_articles.txt", "w") as f:
    for article in articles:
        f.write(article + "\n")
```

### Training Script

```python
from utils.model_utils import train_model

train_model(
    config_name="small",           # Model size
    data_path="./data/your_data.txt",
    output_dir="./checkpoints",
    num_epochs=3,
    batch_size=4,
    learning_rate=3e-4
)
```

### Advanced Training

For more control, use the training pipeline directly:

```python
from training.train_model import ModelTrainer, TrainingArguments
from models.transformer_model import TransformerConfig, TransformerForCausalLM
from models.custom_tokenizer import CustomTokenizer

# Configure training
args = TrainingArguments(
    output_dir="./checkpoints",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=8,
    learning_rate=3e-4,
    weight_decay=0.01,
    max_grad_norm=1.0,
    lr_scheduler_type="cosine",
    warmup_ratio=0.03,
    bf16=True,  # Use bfloat16
    logging_steps=100,
    save_steps=1000,
    wandb_project="transformer-news-training"
)

# Create and train model
# ... (see train_model.py for full example)
```

## Inference and Generation

### Basic Text Generation

```python
from inference.model_inference import TransformerGenerator

# Load model
generator = TransformerGenerator("./checkpoints/final_model")

# Generate text
result = generator.generate(
    prompt="The future of artificial intelligence",
    max_new_tokens=100,
    temperature=0.7,
    top_p=0.9,
    do_sample=True
)

print(result)
```

### Chat Interface

```python
from inference.model_inference import create_chatbot

# Create chatbot
chatbot = create_chatbot(
    model_path="./checkpoints/final_model",
    system_prompt="You are a helpful news assistant."
)

# Chat
response = chatbot.chat("What's the latest in AI research?")
print(response)
```

### Batch Generation

```python
prompts = [
    "Breaking news:",
    "In technology news:",
    "Climate update:"
]

results = generator.batch_generate(
    prompts,
    max_new_tokens=50,
    batch_size=2
)

for prompt, result in zip(prompts, results):
    print(f"Prompt: {prompt}")
    print(f"Generated: {result}\n")
```

## Key Architecture Features

### Grouped Query Attention (GQA)
- Reduces memory usage while maintaining performance
- Configurable number of key-value heads
- Efficient for inference

### Sliding Window Attention
- Handles long sequences efficiently
- Configurable window size (default: 4096)
- Reduces computational complexity

### RMSNorm
- More stable than LayerNorm
- Faster computation
- Better gradient flow

### SwiGLU Activation
- Gated Linear Unit with SiLU activation
- Better performance than standard activations
- Used in feed-forward networks

### Rotary Position Embeddings (RoPE)
- Relative position encoding
- Better handling of long sequences
- No learned position embeddings

## Training Tips

### Memory Optimization
```python
# Enable gradient checkpointing
args.gradient_checkpointing = True

# Use mixed precision
args.bf16 = True  # or args.fp16 = True

# Reduce batch size and increase gradient accumulation
args.per_device_train_batch_size = 1
args.gradient_accumulation_steps = 16
```

### Distributed Training
```bash
# Multi-GPU training
torchrun --nproc_per_node=4 training/train_transformer.py
```

### Monitoring Training
```python
# Enable WandB logging
args.report_to = "wandb"
args.wandb_project = "transformer-training"
args.run_name = "transformer-news-v1"
```

## Customization

### Custom Model Configurations

```python
from config.training_config import TrainingConfig
from dataclasses import dataclass

@dataclass
class CustomTransformerConfig(TrainingConfig):
    """Custom configuration"""
    hidden_size: int = 3072
    intermediate_size: int = 8192
    num_hidden_layers: int = 24
    num_attention_heads: int = 24
    num_key_value_heads: int = 6
    vocab_size: int = 50000
```

### Custom Training Data Processing

```python
class CustomTextDataset(Dataset):
    def __init__(self, texts, tokenizer, max_length=4096):
        # Custom preprocessing logic
        self.examples = self.preprocess(texts, tokenizer, max_length)
    
    def preprocess(self, texts, tokenizer, max_length):
        # Implement custom preprocessing
        pass
```

## Performance Benchmarks

Approximate training speeds (depends on hardware):

| Config | Parameters | GPU Memory | Tokens/sec (A100) |
|--------|------------|------------|-------------------|
| tiny   | 125M       | 2GB        | ~8000             |
| small  | 1B         | 8GB        | ~2000             |
| medium | 3B         | 16GB       | ~800              |
| large  | 7B         | 24GB       | ~400              |

## Integration with News Copilot

This Transformer implementation is designed to integrate with the broader News Copilot system:

1. **Text Generation**: Generate news articles and summaries
2. **Chatbot**: Power the news Q&A system
3. **Classification**: Fine-tune for news categorization
4. **Recommendation**: Generate personalized content

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**:
   - Reduce batch size
   - Enable gradient checkpointing
   - Use smaller model configuration

2. **Slow Training**:
   - Enable mixed precision (bf16/fp16)
   - Increase batch size with gradient accumulation
   - Use distributed training

3. **Poor Generation Quality**:
   - Train for more epochs
   - Adjust learning rate
   - Use larger model configuration
   - Improve training data quality

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test with tiny model first
python utils/transformer_utils.py train --config tiny --epochs 1
```

## Contributing

When modifying the Transformer implementation:

1. Follow the existing code structure
2. Add proper documentation
3. Test with tiny configuration first
4. Update this README if adding new features

## License

This implementation is for the News Copilot project. See the main project license for details.

## References

- [Transformer 7B Paper](https://arxiv.org/abs/2310.06825)
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762)
- [RoFormer: Enhanced Transformer with Rotary Position Embedding](https://arxiv.org/abs/2104.09864)
- [GLU Variants Improve Transformer](https://arxiv.org/abs/2002.05202)
