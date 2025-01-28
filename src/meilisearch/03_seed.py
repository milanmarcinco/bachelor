import json
import math
import struct
import time
from typing import List

from lib.conf import Part, PARTS, MODEL_IDS, MODEL_DETAILS
from lib.meili import client, get_index_name

with open("data/library/metadata.json", "r") as file:
    documents = json.load(file)


def load_parts(document_id: str, part: Part) -> List[str]:
    filepath = f"data/document_parts/json/{document_id}.json"

    with open(filepath, "r") as file:
        parts = json.load(file)

    return parts[part]


def load_vectors(document_id: str, index_name: str, dimensions: int) -> List[List[float]]:
    dir_path = f"data/vectors/{index_name}"
    filepath = f"{dir_path}/{document_id}.bin"

    with open(filepath, "rb") as file:
        vectors = list(
            struct.iter_unpack("d" * dimensions, file.read())
        )

    return vectors


for model_id in MODEL_IDS:
    print(f"[{model_id}]")

    for part in PARTS:
        print(f"[{model_id}][{part}]")
        index_name = get_index_name(part, model_id)
        index = client.index(index_name)

        for idx, document in enumerate(documents[20:]):
            docs_progress = f"{idx+1}/{len(documents)}"
            print(f"[{model_id}][{part}][{docs_progress}]")

            doc_id = document["pk"]
            title = document["title"]

            dimensions = MODEL_DETAILS[model_id]["embedding_size"]

            parts = load_parts(doc_id, part)
            vectors = load_vectors(doc_id, index_name, dimensions)

            batch_size = 32
            batch_count = math.ceil(len(parts) / batch_size)
            for i in range(0, batch_count):

                batch_progress = f"{i+1}/{batch_count}"
                print(f"[{model_id}][{part}][{docs_progress}][{batch_progress}]")

                parts_batch = parts[i * batch_size:(i + 1) * batch_size]
                vectors_batch = vectors[i * batch_size:(i + 1) * batch_size]

                documents_batch = []
                for j in range(len(parts_batch)):
                    serial_number = i * batch_size + j

                    documents_batch.append({
                        "id": f"{doc_id}_{serial_number}",
                        "document_id": doc_id,
                        "text": parts_batch[j],
                        "_vectors": {
                            "default": vectors_batch[j]
                        }
                    })

                try:
                    index.add_documents(documents_batch)
                except Exception as e:
                    # fmt: off
                    print(f"[{model_id}][{part}][{docs_progress}][{batch_progress}]: Error inserting documents: {e}")
                    # fmt: on
