# load_generate_text.py

import torch
from lstm_model import LSTMModel
import json


def load_model(model_path):
    checkpoint = torch.load(model_path)
    model = LSTMModel(
        checkpoint["vocab_size"],
        checkpoint["embedding_dim"],
        checkpoint["hidden_dim"],
        checkpoint["num_layers"],
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model


def load_config(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)
    return config


def generate_text(
    seed_text, next_words, model, word_to_ix, ix_to_word, temperature=1.0, seq_length=10
):
    generated_text = seed_text
    for _ in range(next_words):
        seed_tokens = seed_text.split()
        if len(seed_tokens) < seq_length:
            pad_length = seq_length - len(seed_tokens)
            seed_tokens = ["<pad>"] * pad_length + seed_tokens
        seed_idx = torch.tensor([[word_to_ix.get(word, 0) for word in seed_tokens]])
        with torch.no_grad():
            output = model(seed_idx)

        output_dist = output.squeeze().div(temperature).exp()
        word_idx = torch.multinomial(output_dist, 1).item()

        predicted_word = ix_to_word.get(word_idx, "<unk>")
        generated_text += " " + predicted_word
        seed_text = " ".join(seed_text.split()[1:]) + " " + predicted_word
    return generated_text


def main():
    model_path = "pytorch_model.bin"
    config_path = "config.json"

    model = load_model(model_path)
    config = load_config(config_path)

    vocab_size = config["vocab_size"]
    embedding_dim = config["embedding_dim"]
    hidden_dim = config["hidden_dim"]
    num_layers = config["num_layers"]

    # You may need to define word_to_ix and ix_to_word based on your training data
    word_to_ix = {}
    ix_to_word = {}

    seed_text = "Người dân Quỳnh Đôi không đồng tình ghép tên với xã"
    generated_text = generate_text(
        seed_text, 20, model, word_to_ix, ix_to_word, temperature=1
    )
    print(generated_text)


if __name__ == "__main__":
    main()
