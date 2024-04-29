from transformers import pipeline

try:
    text_generation_pipeline = pipeline(
        "text-generation",
        model="news-copilot-gpt2",
        tokenizer="news-copilot-gpt2",
    )
except Exception as e:
    print("Failed to load text generation pipeline: ", e)
    text_generation_pipeline = None
