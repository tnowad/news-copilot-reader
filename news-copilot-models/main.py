from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    TokenClassificationPipeline,
)

tokenizer = AutoTokenizer.from_pretrained("KoichiYasuoka/bert-base-vietnamese-upos")
model = AutoModelForTokenClassification.from_pretrained(
    "KoichiYasuoka/bert-base-vietnamese-upos"
)
pipeline = TokenClassificationPipeline(
    tokenizer=tokenizer, model=model, aggregation_strategy="simple"
)
nlp = lambda x: [(x[t["start"] : t["end"]], t["entity_group"]) for t in pipeline(x)]
print(nlp("Hai cái đầu thì tốt hơn một."))
