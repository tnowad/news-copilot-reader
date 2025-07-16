"""
Utility scripts for Transformer model training and inference
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Any, Optional

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.transformer_model import TransformerConfig, TransformerForCausalLM
from models.custom_tokenizer import CustomTokenizer, create_custom_tokenizer_from_texts
from config.training_config import get_config
from training.train_model import TransformerTrainer, TrainingArguments, TextDataset, load_training_data
from inference.model_inference import TransformerGenerator, create_model_chatbot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_model(config_name: str = "tiny", save_path: str = "./models/untrained") -> None:
    """Create and save an untrained Transformer model"""
    
    logger.info(f"Creating {config_name} Transformer model...")
    
    # Get configuration
    config = get_config(config_name)
    
    # Create model config
    model_config = TransformerConfig(
        vocab_size=config.vocab_size,
        hidden_size=config.hidden_size,
        intermediate_size=config.intermediate_size,
        num_hidden_layers=config.num_hidden_layers,
        num_attention_heads=config.num_attention_heads,
        num_key_value_heads=config.num_key_value_heads,
        max_position_embeddings=config.max_position_embeddings,
    )
    
    # Create model
    model = TransformerForCausalLM(model_config)
    
    # Save model
    os.makedirs(save_path, exist_ok=True)
    
    # Save model weights
    import torch
    torch.save(model.state_dict(), os.path.join(save_path, "pytorch_model.bin"))
    
    # Save config
    import json
    with open(os.path.join(save_path, "config.json"), "w") as f:
        json.dump(model_config.__dict__, f, indent=2)
    
    logger.info(f"Model saved to {save_path}")
    
    # Print model info
    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Total parameters: {total_params:,}")


def prepare_sample_data(output_file: str = "./data/sample_news.txt") -> None:
    """Create sample news data for training"""
    
    sample_news = [
        "Breaking News: Scientists discover new breakthrough in renewable energy technology that could revolutionize solar power generation.",
        
        "In a major development for artificial intelligence, researchers have announced a new language model that can understand context better than previous systems.",
        
        "The stock market reached new heights today as technology companies reported strong quarterly earnings, with particular growth in cloud computing services.",
        
        "Climate change continues to be a pressing global issue as temperatures rise and extreme weather events become more frequent worldwide.",
        
        "Space exploration took a significant step forward with the successful launch of a new mission to explore the outer planets of our solar system.",
        
        "Healthcare innovation shows promise with the development of new treatment methods for previously incurable diseases using gene therapy techniques.",
        
        "Economic indicators suggest steady growth in the manufacturing sector, with increased production and employment rates across multiple industries.",
        
        "Education systems worldwide are adapting to new technologies, incorporating digital learning tools and remote instruction capabilities.",
        
        "Environmental conservation efforts are gaining momentum as governments and organizations commit to reducing carbon emissions and protecting biodiversity.",
        
        "Sports news: The championship season concluded with record-breaking performances and unprecedented fan engagement across multiple leagues.",
        
        "Technology companies are investing heavily in quantum computing research, potentially leading to revolutionary changes in data processing capabilities.",
        
        "International relations continue to evolve as countries work together on global challenges including pandemic response and economic recovery.",
        
        "Cultural events and arts festivals are returning to normal capacity as communities celebrate creativity and artistic expression after challenging times.",
        
        "Scientific research in medicine has led to new understanding of genetic factors in disease prevention and personalized treatment approaches.",
        
        "Urban development projects focus on sustainability and smart city technologies to improve quality of life for residents in metropolitan areas."
    ]
    
    # Expand each article with more content
    expanded_articles = []
    for article in sample_news:
        # Add more content to each article
        expanded = article + " " + "This development has significant implications for the future. " * 20
        expanded += "Experts in the field are closely monitoring the situation and providing analysis on potential outcomes. " * 10
        expanded += "The public response has been overwhelmingly positive, with many expressing excitement about the possibilities. " * 10
        expanded_articles.append(expanded)
    
    # Create output directory
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        for article in expanded_articles * 50:  # Repeat for more training data
            f.write(article + '\n\n')
    
    logger.info(f"Sample data created: {output_file}")
    logger.info(f"Total articles: {len(expanded_articles) * 50}")


def train_model(
    config_name: str = "tiny",
    data_path: str = "./data/sample_news.txt",
    output_dir: str = "./checkpoints",
    num_epochs: int = 1,
    batch_size: int = 1,
    learning_rate: float = 3e-4
) -> None:
    """Train a Transformer model"""
    
    logger.info(f"Starting training with {config_name} configuration...")
    
    # Prepare sample data if it doesn't exist
    if not os.path.exists(data_path):
        logger.info("Creating sample data...")
        prepare_sample_data(data_path)
    
    # Create tokenizer
    tokenizer_path = os.path.join(output_dir, "tokenizer")
    if not os.path.exists(tokenizer_path):
        logger.info("Creating tokenizer...")
        training_texts = load_training_data(data_path)[:100]  # Use subset for tokenizer
        tokenizer = create_custom_tokenizer_from_texts(
            training_texts,
            model_name="custom_tokenizer",
            vocab_size=32000,
            save_dir=tokenizer_path
        )
    else:
        logger.info("Loading existing tokenizer...")
        tokenizer = CustomTokenizer.from_pretrained(tokenizer_path)
    
    # Get training config
    config = get_config(config_name)
    
    # Create model config
    model_config = TransformerConfig(
        vocab_size=tokenizer.get_vocab_size(),
        hidden_size=config.hidden_size,
        intermediate_size=config.intermediate_size,
        num_hidden_layers=config.num_hidden_layers,
        num_attention_heads=config.num_attention_heads,
        num_key_value_heads=config.num_key_value_heads,
        max_position_embeddings=config.max_position_embeddings,
    )
    
    # Create model
    model = TransformerForCausalLM(model_config)
    
    # Load training data
    training_texts = load_training_data(data_path)
    
    # Create dataset
    train_dataset = TextDataset(
        training_texts,
        tokenizer,
        max_length=512  # Smaller for demo
    )
    
    # Create training arguments
    args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=4,
        learning_rate=learning_rate,
        logging_steps=10,
        save_steps=100,
        max_seq_length=512,
        bf16=False,  # Disable for CPU training
        fp16=False,
        run_name=f"transformer-{config_name}-demo"
    )
    
    # Create trainer
    trainer = TransformerTrainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        tokenizer=tokenizer
    )
    
    # Start training
    trainer.train()
    
    logger.info(f"Training completed! Model saved to {output_dir}")


def test_inference(model_path: str, prompts: Optional[List[str]] = None) -> None:
    """Test model inference"""
    
    if not os.path.exists(model_path):
        logger.error(f"Model not found at {model_path}")
        return
    
    logger.info(f"Loading model from {model_path}")
    
    try:
        generator = TransformerGenerator(model_path, device="cpu", torch_dtype=None)
        
        # Default test prompts
        if prompts is None:
            prompts = [
                "The future of artificial intelligence",
                "Breaking news:",
                "In a recent scientific study,",
                "The impact of technology on",
                "Climate change is"
            ]
        
        logger.info("Testing text generation...")
        
        for prompt in prompts:
            logger.info(f"\nPrompt: {prompt}")
            
            try:
                result = generator.generate(
                    prompt=prompt,
                    max_new_tokens=50,
                    temperature=0.7,
                    do_sample=True
                )
                logger.info(f"Generated: {result}")
            except Exception as e:
                logger.error(f"Generation failed: {e}")
        
        # Test model info
        info = generator.get_model_info()
        logger.info(f"\nModel Info: {info}")
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")


def interactive_chat_cli(model_path: str) -> None:
    """Start interactive chat"""
    
    if not os.path.exists(model_path):
        logger.error(f"Model not found at {model_path}")
        return
    
    try:
        logger.info("Loading model for chat...")
        chatbot = create_model_chatbot(
            model_path,
            system_prompt="You are a helpful AI assistant specialized in news and current events.",
            device="cpu",
            torch_dtype=None
        )
        
        logger.info("Chat started! Type 'quit' to exit, 'clear' to clear history.")
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
                response = chatbot.chat(user_input, max_new_tokens=100)
                print(f"Assistant: {response}")
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        logger.error(f"Failed to start chat: {e}")


def main():
    parser = argparse.ArgumentParser(description="Transformer Model Utilities")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create model command
    create_parser = subparsers.add_parser('create', help='Create untrained model')
    create_parser.add_argument('--config', default='tiny', choices=['tiny', 'small', 'medium', 'large'])
    create_parser.add_argument('--output', default='./models/untrained')
    
    # Prepare data command
    data_parser = subparsers.add_parser('data', help='Prepare sample training data')
    data_parser.add_argument('--output', default='./data/sample_news.txt')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train model')
    train_parser.add_argument('--config', default='tiny', choices=['tiny', 'small', 'medium', 'large'])
    train_parser.add_argument('--data', default='./data/sample_news.txt')
    train_parser.add_argument('--output', default='./checkpoints')
    train_parser.add_argument('--epochs', type=int, default=1)
    train_parser.add_argument('--batch-size', type=int, default=1)
    train_parser.add_argument('--learning-rate', type=float, default=3e-4)
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test model inference')
    test_parser.add_argument('model_path', help='Path to trained model')
    test_parser.add_argument('--prompts', nargs='*', help='Test prompts')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Interactive chat')
    chat_parser.add_argument('model_path', help='Path to trained model')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_model(args.config, args.output)
    
    elif args.command == 'data':
        prepare_sample_data(args.output)
    
    elif args.command == 'train':
        train_model(
            config_name=args.config,
            data_path=args.data,
            output_dir=args.output,
            num_epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate
        )
    
    elif args.command == 'test':
        test_inference(args.model_path, args.prompts)
    
    elif args.command == 'chat':
        interactive_chat_cli(args.model_path)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
