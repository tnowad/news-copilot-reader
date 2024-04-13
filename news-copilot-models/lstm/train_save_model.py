# train_save_model.py

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import json


class TextDataset(Dataset):
    def __init__(self, X, y):
        self.X = X
        self.y = y

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class LSTMModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers):
        super(LSTMModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        embeds = self.embedding(x)
        lstm_out, _ = self.lstm(embeds)
        out = self.fc(lstm_out[:, -1, :])
        return out


def train_model(
    data_loader,
    model,
    criterion,
    optimizer,
    num_epochs,
    seq_length,
    word_to_ix,
    ix_to_word,
    tokenizer_path,
):
    for epoch in range(num_epochs):
        for inputs, labels in data_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        seed_text = "Người dân Quỳnh Đôi không đồng tình ghép tên với xã"
        generated_text = generate_text(
            seed_text, 20, model, word_to_ix, ix_to_word, temperature=1
        )
        print(generated_text)
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "vocab_size": model.embedding.num_embeddings,
            "embedding_dim": model.embedding.embedding_dim,
            "hidden_dim": model.lstm.hidden_size,
            "num_layers": model.lstm.num_layers,
        },
        "pytorch_model.bin",
    )

    with open(tokenizer_path, "w") as f:
        json.dump({"word_to_idx": word_to_ix}, f)


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
    with open("corpus.txt", "r") as file:
        data = file.read()

    words = data.split()
    word_to_ix = {word: i for i, word in enumerate(set(words))}
    ix_to_word = {i: word for word, i in word_to_ix.items()}
    vocab_size = len(word_to_ix)

    data_idx = [word_to_ix[word] for word in words]

    seq_length = 10
    sequences = []
    for i in range(len(data_idx) - seq_length):
        sequences.append(data_idx[i : i + seq_length + 1])

    sequences = np.array(sequences)
    X = torch.from_numpy(sequences[:, :-1])
    y = torch.from_numpy(sequences[:, -1])

    dataset = TextDataset(X, y)
    dataloader = DataLoader(dataset, batch_size=64, shuffle=True)

    embedding_dim = 100
    hidden_dim = 150
    num_layers = 2
    model = LSTMModel(vocab_size, embedding_dim, hidden_dim, num_layers)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.01)

    num_epochs = 1
    tokenizer_path = "tokenizer.json"
    train_model(
        dataloader,
        model,
        criterion,
        optimizer,
        num_epochs,
        seq_length,
        word_to_ix,
        ix_to_word,
        tokenizer_path,
    )


if __name__ == "__main__":
    main()
