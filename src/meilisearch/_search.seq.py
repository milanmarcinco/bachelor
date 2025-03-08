import os
import json
from typing import List

from lib.conf import PARTS, LANGUAGES, MODEL_IDS, MODEL_DETAILS
from lib.meili import get_meilisearch_client, get_index_name
from lib.model import Model


base_dirpath = "data/retrieval"
for model_id in MODEL_IDS:
    dirpath = f"{base_dirpath}/{model_id}"
    os.makedirs(dirpath, exist_ok=True)

with open("data/dataset/02_queries-EN.json", "r") as file:
    en_queries: List[str] = json.load(file)
with open("data/dataset/02_queries-SK.json", "r") as file:
    sk_queries: List[str] = json.load(file)
with open("data/dataset/02_queries-DE.json", "r") as file:
    de_queries: List[str] = json.load(file)

queries_by_language = {
    "en": en_queries,
    "sk": sk_queries,
    "de": de_queries
}

client = get_meilisearch_client()

for model_id in MODEL_IDS:
    embedder = Model(MODEL_DETAILS[model_id])

    for part in PARTS:
        for lang in LANGUAGES:
            queries = queries_by_language[lang]
            vectors = embedder.encode(queries)

            for idx, query in enumerate(queries):
                query_id = idx + 1
                vector = vectors[idx]
                task_id = f"{part}-{lang}-{query_id}"

                print(f"Starting {task_id}")

                index_name = get_index_name(part, model_id)
                index = client.index(index_name)

                response = index.search(None, {
                    "limit": 1000,
                    "showRankingScore": True,
                    "vector": vector,
                    "hybrid": {
                        "embedder": "default",
                        "semanticRatio": 1
                    }
                })

                documents = [
                    {
                        "id": document["document_id"],
                        "similarity": document["_rankingScore"]
                    }
                    for document in response["hits"]
                ]

                task_result = {
                    "task_id": task_id,
                    "part": part,
                    "lang": lang,
                    "query": query,
                    "model_id": model_id,
                    "query_id": query_id,
                    "documents": documents
                }

                dirpath = f"{base_dirpath}/{model_id}"
                filepath = f"{dirpath}/{task_id}.json"
                with open(filepath, "w") as file:
                    json.dump(task_result, file, indent=2, ensure_ascii=False)

                print(f"Finished {task_id}")
