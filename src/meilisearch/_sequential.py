import json
import math
import os
from typing import List

from lib.conf import Part, PARTS, MODEL_IDS, MODEL_DETAILS
from lib.meili import client, get_index_name
from lib.model import Model

with open("data/library/metadata.json", "r") as file:
    documents = json.load(file)


def load_parts(document_id: str, part: Part) -> List[str]:
    filepath = f"data/document_parts/json/{document_id}.json"

    with open(filepath, "r") as file:
        parts = json.load(file)

    return parts[f"{part}s"]


for model_id in MODEL_IDS:
    print(f"[{model_id}]")
    embedder = Model(MODEL_DETAILS[model_id])
    dimensions = MODEL_DETAILS[model_id]["embedding_size"]

    for part in PARTS:
        print(f"[{model_id}][{part}]")
        index_name = get_index_name(part, model_id)
        index = client.index(index_name)
        index.delete_all_documents()

        dir_path = f"data/vectors/{index_name}"
        os.makedirs(dir_path, exist_ok=True)

        for idx, document in enumerate(documents[:3]):
            docs_progress = f"{idx+1}/{len(documents)}"
            print(f"[{model_id}][{part}][{docs_progress}]")

            doc_id = document["pk"]
            title = document["title"]

            parts = load_parts(doc_id, part)

            vectors_batch_size = 8192
            batch_count = math.ceil(len(parts) / vectors_batch_size)

            for i in range(0, batch_count):
                batch_progress = f"{i+1}/{batch_count}"

                print(
                    f"[{model_id}][{part}][{docs_progress}][{batch_progress}]: computing embeddings start"
                )

                parts_batch = parts[
                    i * vectors_batch_size:(i + 1) * vectors_batch_size
                ]

                try:
                    embeddings = embedder.encode(parts_batch)
                except Exception as e:
                    # fmt: off
                    print(f"[{model_id}][{part}][{docs_progress}][{batch_progress}]: Error computing embeddings: {e}")
                    continue
                    # fmt: on

                print(
                    f"[{model_id}][{part}][{docs_progress}][{batch_progress}]: computing embeddings finished"
                )

                doc_batch_size = 32
                batch_count = math.ceil(len(parts) / doc_batch_size)
                for i in range(0, batch_count):
                    batch_progress = f"{i+1}/{batch_count}"

                    print(
                        f"[{model_id}][{part}][{docs_progress}][{batch_progress}]: indexing start"
                    )

                    parts_batch = parts[
                        i * doc_batch_size:(i + 1) * doc_batch_size
                    ]

                    vectors_batch = embeddings[
                        i * doc_batch_size:(i + 1) * doc_batch_size
                    ]

                    documents_batch = []
                    for j in range(len(parts_batch)):
                        serial_number = i * doc_batch_size + j

                        documents_batch.append({
                            "id": f"{doc_id}_{serial_number}",
                            "document_id": doc_id,
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

                    print(
                        f"[{model_id}][{part}][{docs_progress}][{batch_progress}]: indexing finished"
                    )
