import json

from helpers.db import db
from helpers.helpers import now

MAX_CHARS = 80

with open("data/library/metadata.json", "r") as file:
    documents = json.load(file)


def load_parts(document_id, part):
    filepath = f"data/document_parts/json/{document_id}.json"

    with open(filepath, "r") as file:
        parts = json.load(file)

    match part:
        case "sentence":
            return parts["sentences"]
        case "paragraph":
            return parts["paragraphs"]
        case "page":
            return parts["pages"]


for part in ["page", "sentence", "paragraph"]:
    print(now(), f"[{part}]", flush=True)

    for idx, document in enumerate(documents):
        doc_id = document["pk"]
        title = document["title"]

        if len(title) > MAX_CHARS:
            short_title = f"{title[:MAX_CHARS]}..."
        else:
            short_title = title

        progress = f"[{part}][{idx+1}/{len(documents)}]"

        print(
            now(),
            f"{progress}: Processing document {short_title}",
            flush=True
        )

        parts = load_parts(doc_id, part)

        match part:
            case "sentence":
                batch_size = 200
            case "paragraph":
                batch_size = 20
            case "page":
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
                parameters.append(part)
                parameters.append(item)

            db.execute(
                get_query_string(len(batch)),
                parameters
            )

    print(now(), flush=True)
