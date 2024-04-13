from transformers import (
    GPTNeoForCausalLM,
    GPT2Tokenizer,
    TextDataset,
    DataCollatorForLanguageModeling,
)
from transformers import Trainer, TrainingArguments

model_name = "news-copilot-gpt"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPTNeoForCausalLM.from_pretrained(model_name)

train_dataset = TextDataset(tokenizer=tokenizer, file_path="corpus.txt", block_size=128)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir="./gpt-neo-finetuned",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=8,
    save_steps=1000,
    save_total_limit=2,
    prediction_loss_only=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
)

trainer.train()
