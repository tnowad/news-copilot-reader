from transformers import pipeline

try:
    text_generation_pipeline = pipeline(
        "text-generation",
        model="news-copilot-viwiki",
        tokenizer="news-copilot-viwiki",
    )
except Exception as e:
    print("Failed to load text generation pipeline: ", e)
    text_generation_pipeline = None
