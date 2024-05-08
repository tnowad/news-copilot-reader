import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_name = "news-copilot-gpt2"

tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name).to(device)

train_file = "./corpus.txt"

train_dataset = TextDataset(tokenizer=tokenizer, file_path=train_file, block_size=128)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir=f"./{model_name}-finetuned",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    logging_dir="./logs",
    logging_steps=500,
    evaluation_strategy="epoch",
    save_steps=1000,
    warmup_steps=500,
    weight_decay=0.01,
    logging_first_step=True,
    save_total_limit=1,
    dataloader_num_workers=4,
)


def compute_metrics(eval_pred):
    return {"loss": eval_pred.loss}


trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
    compute_metrics=compute_metrics,
)

best_loss = float("inf")

for epoch in range(int(training_args.num_train_epochs)):
    trainer.train()

    evaluation_results = trainer.evaluate()

    if evaluation_results["loss"] < best_loss:
        best_loss = evaluation_results["loss"]
        trainer.save_model(f"{model_name}-finetuned")

        tokenizer.save_pretrained(f"{model_name}-finetuned")

        print(
            f"Model and tokenizer saved at the end of epoch {epoch+1} with loss: {best_loss}"
        )
    else:
        print(f"No improvement in loss at the end of epoch {epoch+1}")

print("Training finished.")
