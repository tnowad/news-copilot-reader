from flask import Blueprint, request, jsonify

generation_bp = Blueprint("generation", __name__)


def generate_text_gpt2(prompt):
    from transformers import GPT2LMHeadModel, GPT2Tokenizer

    model_name = "gpt2"
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)

    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output = model.generate(input_ids, max_length=50, num_return_sequences=1)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    return generated_text


@generation_bp.route("/fill_mask", methods=["POST"])
def fill_mask():
    data = request.json
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "Text field is required"}), 400
    filled_text = generate_text_gpt2(text)
    return jsonify({"filled_text": filled_text})


@generation_bp.route("/generate_text", methods=["POST"])
def generate_text():
    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"error": "Prompt field is required"}), 400
    generated_text = generate_text_gpt2(prompt)
    return jsonify({"generated_text": generated_text})
