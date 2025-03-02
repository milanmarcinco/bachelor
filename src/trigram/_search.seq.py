import json
import os
from typing import List, Tuple
from psycopg2.extensions import connection

from helpers.db import connection_factory


connection = connection_factory()


dirpath = "data/retrieval/tgrm"
os.makedirs(dirpath, exist_ok=True)

with open("data/dataset/02_queries-EN.json", "r") as file:
    en_queries: List[str] = json.load(file)
with open("data/dataset/02_queries-SK.json", "r") as file:
    sk_queries: List[str] = json.load(file)
with open("data/dataset/02_queries-DE.json", "r") as file:
    de_queries: List[str] = json.load(file)

parts = ['paragraph', 'sentence', 'page']
languages = ["en", "sk", "de"]
queries_by_language = {
    "en": en_queries,
    "sk": sk_queries,
    "de": de_queries
}


def search(part: str, query: str):
    try:
        cursor = connection.cursor()

        cursor.execute("""
            SET pg_trgm.similarity_threshold = 0;

            SELECT
                id,
                similarity
            FROM (
                SELECT
                    document_id AS id,
                    MAX(similarity) AS similarity,
                    COUNT(document_id) AS matches
                FROM (
                    SELECT
                        document_id,
                        SIMILARITY(content, %s)
                    FROM
                        document_parts
                    WHERE
                        part = %s
                            AND
                        content %% %s
                )
                GROUP BY
                    document_id
            )
            ORDER BY
                similarity DESC,
                matches DESC,
                id ASC;
        """, (query, part, query))

        results = cursor.fetchall()
        cursor.close()

        return results
    except:
        return None


for part in parts:
    for lang in languages:
        queries = queries_by_language[lang]

        for idx, query in enumerate(queries):
            query_id = idx + 1
            task_id = f"{part}-{lang}-{query_id}"
            batch_id = f"{part}-{lang}"

            print(f"Processing {task_id}")

            result: List[Tuple[str, float]] | None = search(
                part, query
            )

            if result is None:
                print(f"! Failed {task_id}")

            documents = [
                {
                    "id": id,
                    "similarity": similarity
                } for id, similarity in result
            ]

            task_result = {
                "part": part,
                "lang": lang,
                "query": query,
                "query_id": query_id,
                "documents": documents
            }

            filepath = f"{dirpath}/{part}-{lang}-{query_id}.json"
            with open(filepath, "w") as file:
                json.dump(task_result, file, indent=2, ensure_ascii=False)

            print(f"Finished {task_id}")

connection.close()
