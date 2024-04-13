from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
import torch

saved_model_dir = "news-copilot-gpt"
tokenizer = AutoTokenizer.from_pretrained(saved_model_dir)
config = AutoConfig.from_pretrained(saved_model_dir)
config.pad_token_id = config.eos_token_id
model = AutoModelForCausalLM.from_pretrained(saved_model_dir, config=config)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
prompt = "Tiềm năng của trí tuệ nhân tạo"  # your input sentence
input_ids = tokenizer(prompt, return_tensors="pt")["input_ids"].to(device)
max_length = 100
gen_tokens = model.generate(
    input_ids,
    max_length=max_length,
    do_sample=True,
    temperature=0.1,
    top_k=3,
)
gen_text = tokenizer.batch_decode(gen_tokens)[0]
print("Generated text:", gen_text)
