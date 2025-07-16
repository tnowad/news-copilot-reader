"""
Advanced Transformer Training Script
Complete training pipeline for transformer model from scratch
"""

import os
import json
import math
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torch.amp import autocast, GradScaler
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

from models.transformer_model import TransformerConfig, TransformerForCausalLM
from models.custom_tokenizer import CustomTokenizer, create_custom_tokenizer_from_texts


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TrainingArguments:
    """Training configuration arguments"""
    output_dir: str = "./model_trained"
    overwrite_output_dir: bool = False
    
    # Model parameters
    vocab_size: int = 32000
    hidden_size: int = 4096
    intermediate_size: int = 14336
    num_hidden_layers: int = 32
    num_attention_heads: int = 32
    num_key_value_heads: int = 8
    max_position_embeddings: int = 32768
    
    # Training parameters
    num_train_epochs: int = 3
    max_steps: int = -1
    per_device_train_batch_size: int = 1
    per_device_eval_batch_size: int = 1
    gradient_accumulation_steps: int = 8
    learning_rate: float = 3e-4
    weight_decay: float = 0.01
    adam_beta1: float = 0.9
    adam_beta2: float = 0.95
    adam_epsilon: float = 1e-8
    max_grad_norm: float = 1.0
    
    # Scheduler parameters
    lr_scheduler_type: str = "cosine"
    warmup_ratio: float = 0.03
    warmup_steps: int = 0
    
    # Logging and saving
    logging_steps: int = 100
    save_steps: int = 1000
    eval_steps: int = 1000
    save_total_limit: int = 3
    evaluation_strategy: str = "steps"
    
    # Data parameters
    max_seq_length: int = 4096
    block_size: int = 4096
    
    # Mixed precision
    fp16: bool = False
    bf16: bool = True
    
    # Distributed training
    local_rank: int = -1
    ddp_find_unused_parameters: bool = False
    
    # Experiment tracking
    run_name: Optional[str] = None
    wandb_project: Optional[str] = "transformer-news-training"
    report_to: str = "wandb"
    
    def __post_init__(self):
        if self.warmup_steps == 0 and self.warmup_ratio > 0:
            # Will be calculated later based on total steps
            pass


class TextDataset(Dataset):
    """Dataset for language modeling"""
    
    def __init__(
        self,
        texts: List[str],
        tokenizer: CustomTokenizer,
        max_length: int = 4096,
        stride: int = 2048
    ):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.stride = stride
        
        # Tokenize all texts
        logger.info("Tokenizing texts...")
        self.examples = []
        
        for text in texts:
            # Tokenize text
            tokens = tokenizer.encode(text, add_special_tokens=True, max_length=None)
            
            # Split into chunks with stride
            for i in range(0, len(tokens), stride):
                chunk = tokens[i:i + max_length]
                if len(chunk) >= 64:  # Minimum chunk size
                    # Pad if necessary
                    if len(chunk) < max_length:
                        chunk.extend([tokenizer.unk_token_id] * (max_length - len(chunk)))
                    self.examples.append(chunk)
        
        logger.info(f"Created {len(self.examples)} training examples")
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        tokens = self.examples[idx]
        # For causal LM, input and labels are the same (shifted internally in model)
        return {
            "input_ids": torch.tensor(tokens, dtype=torch.long),
            "labels": torch.tensor(tokens, dtype=torch.long)
        }


class TransformerTrainer:
    """Trainer class for Transformer model"""
    
    def __init__(
        self,
        model: TransformerForCausalLM,
        args: TrainingArguments,
        train_dataset: Dataset,
        eval_dataset: Optional[Dataset] = None,
        tokenizer: Optional[CustomTokenizer] = None,
    ):
        self.model = model
        self.args = args
        self.train_dataset = train_dataset
        self.eval_dataset = eval_dataset
        self.tokenizer = tokenizer
        
        # Setup device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        
        # Setup distributed training if needed
        self.is_distributed = self.args.local_rank != -1
        if self.is_distributed:
            self.model = DDP(self.model, find_unused_parameters=self.args.ddp_find_unused_parameters)
        
        # Setup mixed precision
        self.use_amp = self.args.fp16 or self.args.bf16
        if self.use_amp:
            self.scaler = GradScaler()
        
        # Setup data loaders
        self.train_dataloader = self._get_train_dataloader()
        self.eval_dataloader = self._get_eval_dataloader() if eval_dataset else None
        
        # Calculate total steps
        self.total_steps = self._calculate_total_steps()
        if self.args.warmup_steps == 0 and self.args.warmup_ratio > 0:
            self.args.warmup_steps = int(self.total_steps * self.args.warmup_ratio)
        
        # Setup optimizer and scheduler
        self.optimizer = self._create_optimizer()
        self.scheduler = self._create_scheduler()
        
        # Setup logging
        self._setup_logging()
        
        # Training state
        self.global_step = 0
        self.epoch = 0
        self.best_eval_loss = float('inf')
    
    def _get_train_dataloader(self):
        """Create training dataloader"""
        return DataLoader(
            self.train_dataset,
            batch_size=self.args.per_device_train_batch_size,
            shuffle=True,
            num_workers=4,
            pin_memory=True,
            drop_last=True
        )
    
    def _get_eval_dataloader(self):
        """Create evaluation dataloader"""
        if self.eval_dataset is None:
            return None
        
        return DataLoader(
            self.eval_dataset,
            batch_size=self.args.per_device_eval_batch_size,
            shuffle=False,
            num_workers=4,
            pin_memory=True,
            drop_last=False
        )
    
    def _calculate_total_steps(self):
        """Calculate total training steps"""
        if self.args.max_steps > 0:
            return self.args.max_steps
        
        steps_per_epoch = len(self.train_dataloader) // self.args.gradient_accumulation_steps
        return steps_per_epoch * self.args.num_train_epochs
    
    def _create_optimizer(self):
        """Create optimizer"""
        # Separate parameters for weight decay
        decay_parameters = []
        no_decay_parameters = []
        
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                if any(nd in name for nd in ["bias", "norm", "embedding"]):
                    no_decay_parameters.append(param)
                else:
                    decay_parameters.append(param)
        
        optimizer_grouped_parameters = [
            {
                "params": decay_parameters,
                "weight_decay": self.args.weight_decay,
            },
            {
                "params": no_decay_parameters,
                "weight_decay": 0.0,
            },
        ]
        
        return optim.AdamW(
            optimizer_grouped_parameters,
            lr=self.args.learning_rate,
            betas=(self.args.adam_beta1, self.args.adam_beta2),
            eps=self.args.adam_epsilon,
        )
    
    def _create_scheduler(self):
        """Create learning rate scheduler"""
        if self.args.lr_scheduler_type == "cosine":
            return optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=self.total_steps,
                eta_min=self.args.learning_rate * 0.1
            )
        elif self.args.lr_scheduler_type == "linear":
            return optim.lr_scheduler.LinearLR(
                self.optimizer,
                start_factor=1.0,
                end_factor=0.1,
                total_iters=self.total_steps
            )
        else:
            return None
    
    def _setup_logging(self):
        """Setup experiment tracking"""
        if self.args.report_to == "wandb" and WANDB_AVAILABLE:
            wandb.init(
                project=self.args.wandb_project,
                name=self.args.run_name,
                config=self.args.__dict__
            )
    
    def train(self):
        """Main training loop"""
        logger.info("Starting training...")
        logger.info(f"  Num examples = {len(self.train_dataset)}")
        logger.info(f"  Num epochs = {self.args.num_train_epochs}")
        logger.info(f"  Batch size per device = {self.args.per_device_train_batch_size}")
        logger.info(f"  Gradient accumulation steps = {self.args.gradient_accumulation_steps}")
        logger.info(f"  Total optimization steps = {self.total_steps}")
        
        self.model.train()
        total_loss = 0.0
        start_time = time.time()
        
        for epoch in range(self.args.num_train_epochs):
            self.epoch = epoch
            epoch_loss = 0.0
            
            for step, batch in enumerate(self.train_dataloader):
                # Move batch to device
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                # Forward pass
                with autocast(device_type='cuda', dtype=torch.bfloat16 if self.args.bf16 else torch.float16, 
                            enabled=self.use_amp):
                    outputs = self.model(**batch)
                    loss = outputs["loss"]
                    
                    # Scale loss for gradient accumulation
                    loss = loss / self.args.gradient_accumulation_steps
                
                # Backward pass
                if self.use_amp:
                    self.scaler.scale(loss).backward()
                else:
                    loss.backward()
                
                total_loss += loss.item()
                epoch_loss += loss.item()
                
                # Update weights
                if (step + 1) % self.args.gradient_accumulation_steps == 0:
                    if self.use_amp:
                        self.scaler.unscale_(self.optimizer)
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.args.max_grad_norm)
                        self.scaler.step(self.optimizer)
                        self.scaler.update()
                    else:
                        torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.args.max_grad_norm)
                        self.optimizer.step()
                    
                    if self.scheduler:
                        self.scheduler.step()
                    
                    self.optimizer.zero_grad()
                    self.global_step += 1
                    
                    # Logging
                    if self.global_step % self.args.logging_steps == 0:
                        avg_loss = total_loss / self.args.logging_steps
                        current_lr = self.optimizer.param_groups[0]['lr']
                        elapsed_time = time.time() - start_time
                        
                        logger.info(
                            f"Step {self.global_step} | "
                            f"Loss: {avg_loss:.4f} | "
                            f"LR: {current_lr:.2e} | "
                            f"Time: {elapsed_time:.2f}s"
                        )
                        
                        if WANDB_AVAILABLE and self.args.report_to == "wandb":
                            wandb.log({
                                "train_loss": avg_loss,
                                "learning_rate": current_lr,
                                "epoch": epoch,
                                "global_step": self.global_step
                            })
                        
                        total_loss = 0.0
                        start_time = time.time()
                    
                    # Evaluation
                    if self.eval_dataloader and self.global_step % self.args.eval_steps == 0:
                        eval_loss = self.evaluate()
                        logger.info(f"Eval loss: {eval_loss:.4f}")
                        
                        if WANDB_AVAILABLE and self.args.report_to == "wandb":
                            wandb.log({"eval_loss": eval_loss})
                        
                        # Save best model
                        if eval_loss < self.best_eval_loss:
                            self.best_eval_loss = eval_loss
                            self.save_model(os.path.join(self.args.output_dir, "best_model"))
                    
                    # Save checkpoint
                    if self.global_step % self.args.save_steps == 0:
                        self.save_model(os.path.join(self.args.output_dir, f"checkpoint-{self.global_step}"))
                    
                    # Check if we've reached max steps
                    if self.args.max_steps > 0 and self.global_step >= self.args.max_steps:
                        break
            
            logger.info(f"Epoch {epoch} completed. Avg loss: {epoch_loss / len(self.train_dataloader):.4f}")
            
            if self.args.max_steps > 0 and self.global_step >= self.args.max_steps:
                break
        
        # Save final model
        self.save_model(os.path.join(self.args.output_dir, "final_model"))
        logger.info("Training completed!")
    
    def evaluate(self):
        """Evaluate the model"""
        if self.eval_dataloader is None:
            return float('inf')
        
        self.model.eval()
        total_loss = 0.0
        total_steps = 0
        
        with torch.no_grad():
            for batch in self.eval_dataloader:
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                with autocast(device_type='cuda', dtype=torch.bfloat16 if self.args.bf16 else torch.float16,
                            enabled=self.use_amp):
                    outputs = self.model(**batch)
                    loss = outputs["loss"]
                
                total_loss += loss.item()
                total_steps += 1
        
        self.model.train()
        return total_loss / total_steps
    
    def save_model(self, output_dir: str):
        """Save model and tokenizer"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save model state dict
        model_to_save = self.model.module if hasattr(self.model, 'module') else self.model
        torch.save(model_to_save.state_dict(), os.path.join(output_dir, "pytorch_model.bin"))
        
        # Save config
        config_dict = model_to_save.config.__dict__
        with open(os.path.join(output_dir, "config.json"), "w") as f:
            json.dump(config_dict, f, indent=2)
        
        # Save tokenizer if available
        if self.tokenizer:
            self.tokenizer.save_pretrained(output_dir)
        
        # Save training args
        with open(os.path.join(output_dir, "training_args.json"), "w") as f:
            json.dump(self.args.__dict__, f, indent=2)
        
        logger.info(f"Model saved to {output_dir}")


def load_training_data(data_path: str) -> List[str]:
    """Load training data from various formats"""
    texts = []
    
    if data_path.endswith('.txt'):
        with open(data_path, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f if line.strip()]
    
    elif data_path.endswith('.json'):
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                texts = [item if isinstance(item, str) else str(item) for item in data]
            elif isinstance(data, dict):
                # Assume format like {"texts": [...]}
                texts = data.get("texts", [])
    
    elif data_path.endswith('.jsonl'):
        with open(data_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line.strip())
                if isinstance(data, dict):
                    # Extract text field (adapt based on your data format)
                    text = data.get('text', data.get('content', str(data)))
                    texts.append(text)
                else:
                    texts.append(str(data))
    
    return texts


def main():
    """Main training function"""
    # Parse arguments (in practice, you'd use argparse)
    args = TrainingArguments()
    
    # Setup output directory
    os.makedirs(args.output_dir, exist_ok=args.overwrite_output_dir)
    
    # Load or create tokenizer
    logger.info("Setting up tokenizer...")
    tokenizer_path = "./tokenizer"
    if os.path.exists(tokenizer_path):
        tokenizer = CustomTokenizer.from_pretrained(tokenizer_path)
    else:
        # Create tokenizer from training data
        logger.info("Creating tokenizer from training data...")
        training_texts = load_training_data("./training_data.txt")  # Adjust path
        tokenizer = create_custom_tokenizer_from_texts(
            training_texts[:10000],  # Use subset for tokenizer training
            model_name="custom_tokenizer",
            vocab_size=args.vocab_size,
            save_dir=tokenizer_path
        )
    
    # Create model config
    config = TransformerConfig(
        vocab_size=tokenizer.get_vocab_size(),
        hidden_size=args.hidden_size,
        intermediate_size=args.intermediate_size,
        num_hidden_layers=args.num_hidden_layers,
        num_attention_heads=args.num_attention_heads,
        num_key_value_heads=args.num_key_value_heads,
        max_position_embeddings=args.max_position_embeddings,
    )
    
    # Create model
    logger.info("Creating model...")
    model = TransformerForCausalLM(config)
    
    # Load training data
    logger.info("Loading training data...")
    training_texts = load_training_data("./training_data.txt")  # Adjust path
    
    # Create datasets
    train_dataset = TextDataset(
        training_texts[:-1000],  # All but last 1000 for training
        tokenizer,
        max_length=args.max_seq_length
    )
    
    eval_dataset = TextDataset(
        training_texts[-1000:],  # Last 1000 for evaluation
        tokenizer,
        max_length=args.max_seq_length
    ) if len(training_texts) > 1000 else None
    
    # Create trainer
    trainer = TransformerTrainer(
        model=model,
        args=args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer
    )
    
    # Start training
    trainer.train()


if __name__ == "__main__":
    main()
