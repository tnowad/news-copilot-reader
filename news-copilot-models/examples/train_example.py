#!/usr/bin/env python3
"""
Example training script for Transformer model
This script demonstrates how to train a Transformer model from scratch
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from models.transformer_model import TransformerConfig, TransformerForCausalLM
from models.custom_tokenizer import CustomTokenizer, create_custom_tokenizer_from_texts
from config.training_config import get_config
from training.train_model import TransformerTrainer, TrainingArguments, TextDataset, load_training_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def prepare_news_data():
    """Prepare sample news data for training"""
    
    # Create comprehensive news dataset
    news_articles = [
        # Technology News
        "Breaking: Revolutionary AI breakthrough announced by leading tech company. "
        "The new artificial intelligence system demonstrates unprecedented capabilities in natural language understanding. "
        "Researchers report significant improvements in processing complex queries and generating human-like responses. "
        "This advancement could transform how we interact with digital assistants and automated systems. "
        "Industry experts predict widespread adoption across multiple sectors including healthcare, education, and finance. "
        "The development team spent three years perfecting the underlying algorithms and neural network architecture. "
        "Initial testing shows remarkable accuracy in understanding context and maintaining coherent conversations. "
        "The technology will be gradually integrated into existing products over the next two years.",
        
        # Business News  
        "Stock markets reach record highs as technology sector shows strong quarterly growth. "
        "Major corporations report increased revenue driven by digital transformation initiatives. "
        "Cloud computing services continue to experience unprecedented demand from businesses worldwide. "
        "Investment analysts recommend diversified portfolios including both traditional and emerging technology stocks. "
        "Economic indicators suggest sustained growth despite global uncertainties and market volatility. "
        "Consumer spending patterns show increased preference for digital services and online platforms. "
        "Corporate earnings exceed expectations with particular strength in software and semiconductor companies. "
        "Market experts anticipate continued expansion in the technology and healthcare sectors.",
        
        # Science News
        "Groundbreaking medical research reveals new treatment options for previously incurable diseases. "
        "Scientists develop innovative gene therapy techniques showing promising results in clinical trials. "
        "The research team collaborated with international institutions to validate their findings. "
        "Patient outcomes demonstrate significant improvement with minimal side effects reported. "
        "This breakthrough could benefit millions of people suffering from genetic disorders worldwide. "
        "Regulatory approval processes are underway in multiple countries for rapid deployment. "
        "Medical professionals express optimism about the potential to revolutionize healthcare treatment. "
        "Further studies will explore applications for other conditions and expand treatment options.",
        
        # Environmental News
        "Climate change research presents urgent call for immediate action on carbon emissions. "
        "International scientists warn of accelerating global temperature increases and extreme weather patterns. "
        "Renewable energy adoption shows promising growth with solar and wind power leading the transition. "
        "Government policies and corporate initiatives focus on achieving net-zero emissions by 2050. "
        "Environmental conservation efforts gain momentum through community engagement and awareness campaigns. "
        "Innovative technologies emerge to capture carbon dioxide and reduce atmospheric greenhouse gases. "
        "Sustainable development practices become essential for businesses across all industries. "
        "Climate adaptation strategies help communities prepare for changing environmental conditions.",
        
        # Politics News
        "International summit addresses global cooperation on trade and economic development policies. "
        "World leaders discuss strategies for promoting peace and stability in conflict-affected regions. "
        "Diplomatic negotiations continue on critical issues affecting international relations and security. "
        "Policy makers work to balance economic growth with environmental protection and social welfare. "
        "Democratic processes strengthen through increased civic engagement and voter participation. "
        "Legislative reforms aim to improve transparency and accountability in government institutions. "
        "International organizations facilitate dialogue between nations on shared challenges and opportunities. "
        "Political stability remains crucial for sustained economic development and social progress.",
        
        # Sports News
        "Championship season concludes with record-breaking performances and unprecedented fan engagement. "
        "Athletes demonstrate exceptional skill and dedication throughout the competitive tournament. "
        "Sports technology enhances training methods and performance analysis for professional teams. "
        "Youth development programs inspire the next generation of talented athletes and sports enthusiasts. "
        "International competitions promote cultural exchange and friendly rivalry between nations. "
        "Sports medicine advances help athletes recover faster and prevent career-ending injuries. "
        "Broadcasting innovations provide immersive viewing experiences for millions of fans worldwide. "
        "Community sports programs encourage healthy lifestyles and social connection among participants.",
        
        # Health News
        "Public health initiatives focus on preventive care and wellness programs for diverse communities. "
        "Medical professionals advocate for increased mental health awareness and accessible treatment options. "
        "Healthcare systems adapt to changing demographics and emerging health challenges. "
        "Telemedicine platforms expand access to medical consultations in remote and underserved areas. "
        "Pharmaceutical research develops targeted therapies for complex chronic conditions. "
        "Health education campaigns promote lifestyle changes that reduce disease risk factors. "
        "Medical devices incorporate artificial intelligence to improve diagnostic accuracy and patient monitoring. "
        "Healthcare policy reforms aim to reduce costs while maintaining high-quality patient care.",
        
        # Education News
        "Educational institutions embrace digital learning technologies to enhance student outcomes. "
        "Remote learning platforms provide flexible access to quality education worldwide. "
        "Teachers receive professional development training in innovative pedagogical methods. "
        "Student assessment methods evolve to measure practical skills and creative problem-solving abilities. "
        "Educational equity initiatives ensure all students have access to learning opportunities. "
        "STEM education programs prepare students for careers in science, technology, engineering, and mathematics. "
        "International education exchanges promote cultural understanding and global citizenship. "
        "Lifelong learning becomes essential as rapidly changing job markets require continuous skill development."
    ]
    
    # Expand articles with additional content
    expanded_articles = []
    for article in news_articles:
        # Add context and analysis
        expanded = article + "\n\n"
        expanded += "This development has significant implications for stakeholders across multiple sectors. "
        expanded += "Industry analysts are closely monitoring the situation and providing detailed assessments. "
        expanded += "The long-term impact on society and economic markets remains to be fully understood. "
        expanded += "Experts recommend staying informed about ongoing developments and potential changes. "
        expanded += "Public response has been mixed, with various groups expressing different perspectives. "
        expanded += "Policy implications may require legislative review and regulatory adjustments. "
        expanded += "International cooperation will be essential for addressing global aspects of this issue. "
        expanded += "Continued research and analysis will provide better understanding of complex factors involved. "
        expanded += "Stakeholder engagement ensures all voices are heard in the decision-making process. "
        expanded += "Future developments will likely build upon these initial findings and recommendations.\n"
        
        expanded_articles.append(expanded)
    
    return expanded_articles


def create_training_data(output_file: str = "data/news_training.txt", num_copies: int = 100):
    """Create comprehensive training dataset"""
    
    logger.info("Preparing comprehensive news training data...")
    
    # Get base articles
    articles = prepare_news_data()
    
    # Create output directory
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write training data
    with open(output_file, 'w', encoding='utf-8') as f:
        for _ in range(num_copies):  # Repeat articles for more training data
            for article in articles:
                f.write(article + "\n\n")
    
    logger.info(f"Training data created: {output_file}")
    logger.info(f"Total articles: {len(articles) * num_copies}")
    
    return output_file


def main():
    """Main training pipeline"""
    
    logger.info("Starting Transformer training example...")
    
    # Configuration
    config_name = "tiny"  # Start with tiny for demonstration
    model_name = "transformer-news-demo"
    
    # Paths
    data_file = "data/news_training.txt"
    tokenizer_dir = f"models/{model_name}-tokenizer"
    checkpoint_dir = f"checkpoints/{model_name}"
    
    # Step 1: Prepare training data
    logger.info("Step 1: Preparing training data...")
    if not os.path.exists(data_file):
        create_training_data(data_file, num_copies=50)  # Smaller dataset for demo
    
    # Step 2: Create or load tokenizer
    logger.info("Step 2: Setting up tokenizer...")
    if not os.path.exists(tokenizer_dir):
        logger.info("Creating new tokenizer...")
        training_texts = load_training_data(data_file)[:200]  # Use subset for tokenizer
        tokenizer = create_custom_tokenizer_from_texts(
            training_texts,
            model_name=f"{model_name}_tokenizer",
            vocab_size=32000,
            save_dir=tokenizer_dir
        )
    else:
        logger.info("Loading existing tokenizer...")
        tokenizer = CustomTokenizer.from_pretrained(tokenizer_dir)
    
    # Step 3: Configure model
    logger.info("Step 3: Configuring model...")
    training_config = get_config(config_name)
    
    model_config = TransformerConfig(
        vocab_size=tokenizer.get_vocab_size(),
        hidden_size=training_config.hidden_size,
        intermediate_size=training_config.intermediate_size,
        num_hidden_layers=training_config.num_hidden_layers,
        num_attention_heads=training_config.num_attention_heads,
        num_key_value_heads=training_config.num_key_value_heads,
        max_position_embeddings=training_config.max_position_embeddings,
    )
    
    # Step 4: Create model
    logger.info("Step 4: Creating model...")
    model = TransformerForCausalLM(model_config)
    
    # Print model info
    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Model parameters: {total_params:,}")
    
    # Step 5: Prepare dataset
    logger.info("Step 5: Preparing dataset...")
    training_texts = load_training_data(data_file)
    
    # Split data
    split_idx = int(0.9 * len(training_texts))
    train_texts = training_texts[:split_idx]
    eval_texts = training_texts[split_idx:]
    
    train_dataset = TextDataset(
        train_texts,
        tokenizer,
        max_length=512,  # Smaller context for demo
        stride=256
    )
    
    eval_dataset = TextDataset(
        eval_texts,
        tokenizer,
        max_length=512,
        stride=256
    ) if eval_texts else None
    
    logger.info(f"Training examples: {len(train_dataset)}")
    if eval_dataset:
        logger.info(f"Evaluation examples: {len(eval_dataset)}")
    
    # Step 6: Configure training
    logger.info("Step 6: Configuring training...")
    args = TrainingArguments(
        output_dir=checkpoint_dir,
        overwrite_output_dir=True,
        
        # Training parameters
        num_train_epochs=2,  # Small number for demo
        max_steps=-1,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=4,
        
        # Optimization
        learning_rate=3e-4,
        weight_decay=0.01,
        adam_beta1=0.9,
        adam_beta2=0.95,
        max_grad_norm=1.0,
        
        # Scheduler
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        
        # Logging and evaluation
        logging_steps=10,
        eval_steps=50,
        save_steps=50,
        save_total_limit=3,
        evaluation_strategy="steps",
        
        # Hardware
        fp16=False,  # Disable for CPU training
        bf16=False,
        
        # Experiment tracking
        run_name=f"{model_name}-example",
        wandb_project="transformer-news-demo",
        report_to="none",  # Disable wandb for demo
        
        # Model specific
        max_seq_length=512,
    )
    
    # Step 7: Create trainer
    logger.info("Step 7: Creating trainer...")
    trainer = TransformerTrainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
    )
    
    # Step 8: Start training
    logger.info("Step 8: Starting training...")
    try:
        trainer.train()
        logger.info("Training completed successfully!")
        
        # Test the trained model
        logger.info("Testing the trained model...")
        test_prompts = [
            "Breaking news:",
            "In technology developments,",
            "Climate change research shows",
            "Healthcare innovations include"
        ]
        
        # Simple test (without full inference pipeline)
        model.eval()
        for prompt in test_prompts:
            input_ids = tokenizer.encode(prompt, add_special_tokens=True)
            logger.info(f"Test prompt: {prompt}")
            logger.info(f"Tokenized length: {len(input_ids)}")
            
    except Exception as e:
        logger.error(f"Training failed: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("Training example completed!")


if __name__ == "__main__":
    main()
