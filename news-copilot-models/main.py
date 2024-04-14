import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

tokenizer = GPT2Tokenizer.from_pretrained("danghuy1999/gpt2-viwiki")
model = GPT2LMHeadModel.from_pretrained("danghuy1999/gpt2-viwiki").to(device)

text = "Github là gì?"
input_ids = tokenizer.encode(text, return_tensors="pt").to(device)
max_length = 100

sample_outputs = model.generate(
    input_ids,
    pad_token_id=tokenizer.eos_token_id,
    temperature=0.7,
    do_sample=True,
    max_length=max_length,
    min_length=max_length,
    top_k=40,
    num_beams=5,
    early_stopping=True,
    no_repeat_ngram_size=2,
    num_return_sequences=3,
)

for i, sample_output in enumerate(sample_outputs):
    print(
        ">> Generated text {}\n\n{}".format(
            i + 1, tokenizer.decode(sample_output.tolist())
        )
    )
    print("\n---")
