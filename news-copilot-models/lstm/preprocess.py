from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TokenClassificationPipeline,
)
import json
import concurrent.futures

tokenizer = AutoTokenizer.from_pretrained("KoichiYasuoka/bert-base-vietnamese-upos")
model = AutoModelForTokenClassification.from_pretrained(
    "KoichiYasuoka/bert-base-vietnamese-upos"
)
pipeline = TokenClassificationPipeline(
    tokenizer=tokenizer, model=model, aggregation_strategy="simple"
)


def preprocess_sentence(sentence):
    tokenized_output = pipeline(sentence)
    return [(token["word"], token["entity_group"]) for token in tokenized_output]


corpus_file = "corpus-title.txt"
with open(corpus_file, "r", encoding="utf-8") as f:
    corpus = f.readlines()


def process_sentences(chunk):
    preprocessed_chunk = [preprocess_sentence(sentence.strip()) for sentence in chunk]
    return preprocessed_chunk


chunk_size = 100  # Number of sentences to process per chunk
chunks = [corpus[i : i + chunk_size] for i in range(0, len(corpus), chunk_size)]

preprocessed_corpus = []
processed_sentences = 0
percent_completed_last_saved = 0


def save_preprocessed_data(preprocessed_data, percentage_completed):
    output_file = f"preprocessed_data_{int(percentage_completed)}_percent.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(preprocessed_data, f, ensure_ascii=False, indent=4)
    print(f"Saved preprocessed data at {percentage_completed:.2f}% completion")


with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(process_sentences, chunk) for chunk in chunks]
    for future in concurrent.futures.as_completed(futures):
        preprocessed_chunk = future.result()
        preprocessed_corpus.extend(preprocessed_chunk)
        processed_sentences += len(preprocessed_chunk)
        percentage_completed = (processed_sentences / len(corpus)) * 100

        # Check if we have completed an additional 10 percent
        if percentage_completed - percent_completed_last_saved >= 1:
            save_preprocessed_data(preprocessed_corpus, percentage_completed)
            percent_completed_last_saved = percentage_completed

# Save the final preprocessed data
output_file = "preprocessed_data.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(preprocessed_corpus, f, ensure_ascii=False, indent=4)

print("\nPreprocessed data saved to:", output_file)
