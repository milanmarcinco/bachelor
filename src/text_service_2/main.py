import json
import os
from extractor import extract

os.makedirs("output", exist_ok=True)

with open("../../dataset/merged.json") as file:
    documents = json.load(file)

for document in documents:
    id = document["pk"]

    with open(f"output/{id}.txt", "r") as file:
        text = file.read()

    sentences, paragraphs, pages = extract(text)

    with open(f"output/{id}.json", "w") as file:
        json.dump({
            "sentences": sentences,
            "paragraphs": paragraphs,
            "pages": pages
        }, file, indent=4, ensure_ascii=False)
