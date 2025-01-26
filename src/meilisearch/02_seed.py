import json
import uuid
import math
from typing import List, Tuple
from numpy import ndarray

from lib.conf import Part, PARTS, MODEL_IDS, MODEL_DETAILS
from lib.meili import client, get_index_name
from lib.model import Model

with open("data/library/metadata.json", "r") as file:
    documents = json.load(file)


def load_parts(document_id: str, part: Part) -> List[str]:
    filepath = f"data/document_parts/json/{document_id}.json"

    with open(filepath, "r") as file:
        parts = json.load(file)

    return parts[part]


for model_id in MODEL_IDS:
    print(f"[{model_id}]")
    embedder = Model(MODEL_DETAILS[model_id])

    for part in PARTS:
        print(f"[{model_id}][{part}]")
        index_name = get_index_name(part, model_id)
        index = client.index(index_name)

        for idx, document in enumerate(documents):
            docs_progress = f"{idx+1}/{len(documents)}"
            print(f"[{model_id}][{part}][{docs_progress}]")

            doc_id = document["pk"]
            title = document["title"]

            parts = load_parts(doc_id, part)

            batch_size = 32
            batch_count = math.ceil(len(parts) / batch_size)
            for i in range(0, batch_count):
                batch_progress = f"{i+1}/{batch_count}"
                print(f"[{model_id}][{part}][{docs_progress}][{batch_progress}]")

                parts_batch = parts[i * batch_size:(i + 1) * batch_size]
                try:
                    embeddings: ndarray[
                        Tuple[int, int],
                        float
                    ] = embedder.encode(parts_batch)
                except Exception as e:
                    # fmt: off
                    print(f"[{model_id}][{part}][{docs_progress}][{batch_progress}]: Error computing embeddings: {e}")
                    continue
                    # fmt: on

                documents_batch = []
                for i in range(len(parts_batch)):
                    embedding: ndarray[Tuple[int], float] = embeddings[i]
                    vector: List[float] = embedding.tolist()

                    documents_batch.append({
                        "id": str(uuid.uuid4()),
                        "document_id": doc_id,
                        "text": parts_batch[i],
                        "_vectors": {
                            "default": vector
                        }
                    })

                try:
                    index.add_documents(documents_batch)
                except Exception as e:
                    # fmt: off
                    print(f"[{model_id}][{part}][{docs_progress}][{batch_progress}]: Error inserting documents: {e}")
                    # fmt: on
