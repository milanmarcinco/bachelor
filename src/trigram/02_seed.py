import json
from helpers.db import db

with open("data/library/metadata.json", "r") as file:
    documents = json.load(file)


def load_parts(document_id):
    filepath = f"data/document_parts/json/{document_id}.json"

    with open(filepath, "r") as file:
        parts = json.load(file)

    sentences = parts["sentences"]
    paragraphs = parts["paragraphs"]
    pages = parts["pages"]

    return sentences, paragraphs, pages


for idx, document in enumerate(documents):
    doc_id = document["pk"]
    title = document["title"]

    print(f"[{idx+1}/{len(documents)}] Processing document {document['title']}")

    sentences, paragraphs, pages = load_parts(doc_id)

    sentences_batch_size = 200
    paragraphs_batch_size = 20
    pages_batch_size = 10

    sentence_batches = [sentences[i:i+sentences_batch_size]
                        for i in range(0, len(sentences), sentences_batch_size)]

    paragraph_batches = [paragraphs[i:i+paragraphs_batch_size]
                         for i in range(0, len(paragraphs), paragraphs_batch_size)]

    page_batches = [pages[i:i+pages_batch_size]
                    for i in range(0, len(pages), pages_batch_size)]

    def get_query_string(batch_size):
        return f"""
            INSERT INTO document_parts (document_id, part, content) VALUES
            {", ".join(["(%s, %s, %s)"] * batch_size)};
        """

    db.execute(
        """INSERT INTO documents (id, title) VALUES(%s, %s)""",
        (doc_id, title)
    )

    for batch in sentence_batches:
        parameters = []

        for sentence in batch:
            parameters.append(doc_id)
            parameters.append("sentence")
            parameters.append(sentence)

        db.execute(
            get_query_string(len(batch)),
            parameters
        )

    for batch in paragraph_batches:
        parameters = []

        for paragraph in batch:
            parameters.append(doc_id)
            parameters.append("paragraph")
            parameters.append(paragraph)

        db.execute(
            get_query_string(len(batch)),
            parameters
        )

    for batch in page_batches:
        parameters = []

        for page in batch:
            parameters.append(doc_id)
            parameters.append("page")
            parameters.append(page)

        db.execute(
            get_query_string(len(batch)),
            parameters
        )
