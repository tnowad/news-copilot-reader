from unidecode import unidecode
import re


def generate_slug(text):
    text = re.sub(r"[^\w\s-]", "", text)
    return unidecode(text).lower().replace(" ", "-")
