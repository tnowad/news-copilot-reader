import random
import json
import pickle
import numpy as np
import tensorflow as tf

import nltk
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
intents = json.loads(
    open(
        "/home/huy/Documents/dataCode/python/news-copilot-reader/news-copilot-models/chatbotPython/intents.json"
    ).read()
)

words = pickle.load(
    open(
        "/home/huy/Documents/dataCode/python/news-copilot-reader/news-copilot-models/chatbotPython/words.pkl",
        "rb",
    )
)
classes = pickle.load(
    open(
        "/home/huy/Documents/dataCode/python/news-copilot-reader/news-copilot-models/chatbotPython/classes.pkl",
        "rb",
    )
)
model = tf.keras.models.load_model(
    "/home/huy/Documents/dataCode/python/news-copilot-reader/news-copilot-models/chatbotPython/chatbot_model.h5"
)


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)


def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponseChatBot(intent_list, intent_json):
    tag = intent_list[0]["intent"]
    list_of_intents = intent_json["intents"]
    for i in list_of_intents:
        if i["tag"] == tag:
            result = random.choice(i["responses"])
            break
    return result
