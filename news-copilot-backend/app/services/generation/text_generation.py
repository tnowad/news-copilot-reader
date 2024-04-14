from transformers import pipeline

try:
    text_generation_pipeline = pipeline(
        "text-generation",
        model="imthanhlv/gpt2news",
        tokenizer="imthanhlv/gpt2news",
    )
except Exception as e:
    print("Failed to load text generation pipeline: ", e)
    text_generation_pipeline = None
