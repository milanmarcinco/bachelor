import json

from helpers.db import db
from helpers.helpers import now

MAX_CHARS = 80
UNIT = ["page", "sentence", "paragraph"][0]

with open("data/library/metadata.json", "r") as file:
    documents = json.load(file)


def load_parts(document_id, part):
    filepath = f"data/document_parts/json/{document_id}.json"

    with open(filepath, "r") as file:
        parts = json.load(file)

    if part == "sentence":
        return parts["sentences"]
    elif part == "paragraph":
        return parts["paragraphs"]
    elif part == "page":
        return parts["pages"]


print(now(), f"[{UNIT}]", flush=True)

for idx, document in enumerate(documents):
    doc_id = document["pk"]
    title = document["title"]

    if len(title) > MAX_CHARS:
        short_title = f"{title[:MAX_CHARS]}..."
    else:
        short_title = title

    progress = f"[{UNIT}][{idx+1}/{len(documents)}]"

    print(
        now(),
        f"{progress}: Processing document {short_title}",
        flush=True
    )

    parts = load_parts(doc_id, UNIT)

    if UNIT == "sentence":
        batch_size = 200
    elif UNIT == "paragraph":
        batch_size = 20
    elif UNIT == "page":
        batch_size = 10

    batches = [
        parts[i:i+batch_size]
        for i in range(0, len(parts), batch_size)
    ]

    def get_query_string(batch_size):
        return f"""
            INSERT INTO document_parts (document_id, part, content) VALUES
            {", ".join(["(%s, %s, %s)"] * batch_size)};
        """

    for batch in batches:
        parameters = []

        for item in batch:
            parameters.append(doc_id)
            parameters.append(UNIT)
            parameters.append(item)

        db.execute(
            get_query_string(len(batch)),
            parameters
        )

print(now(), flush=True)
