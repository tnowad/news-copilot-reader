import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments

# Check device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load tokenizer and model
tokenizer = GPT2Tokenizer.from_pretrained("news-copilot-viwiki")
model = GPT2LMHeadModel.from_pretrained("news-copilot-viwiki").to(device)

# Path to your training dataset
train_file = "./corpus.txt"

# Load dataset
train_dataset = TextDataset(
    tokenizer=tokenizer, file_path=train_file, block_size=128  # Adjust as needed
)

# Data collator for language modeling
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Training arguments
training_args = TrainingArguments(
    output_dir="./gpt2-finetuned",
    overwrite_output_dir=True,
    num_train_epochs=1,  # Reduce epochs for faster training
    per_device_train_batch_size=2,  # Reduce batch size
    per_device_eval_batch_size=2,  # Reduce batch size
    logging_dir="./logs",
    logging_steps=100,  # Reduce logging frequency
    evaluation_strategy="steps",
    eval_steps=500,  # Reduce evaluation frequency
    save_steps=500,  # Reduce saving frequency
    warmup_steps=100,  # Reduce warmup steps
    weight_decay=0.01,
    logging_first_step=True,
    save_total_limit=1,  # Save only one model checkpoint
    dataloader_num_workers=1,  # Reduce number of workers to 1 for dataloading
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
)

# Train the model
trainer.train()

# Save the fine-tuned model
trainer.save_model("./gpt2-finetuned")

# Save tokenizer
tokenizer.save_pretrained("./gpt2-finetuned")

print("Model and tokenizer saved to: ./gpt2-finetuned")
