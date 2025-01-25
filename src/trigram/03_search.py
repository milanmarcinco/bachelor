import json
from typing import List
from helpers.db import db


with open("/data/dataset/02_queries-EN.json", "r") as file:
    en_queries: List[str] = json.load(file)
with open("/data/dataset/02_queries-SK.json", "r") as file:
    sk_queries: List[str] = json.load(file)
with open("/data/dataset/02_queries-DE.json", "r") as file:
    de_queries: List[str] = json.load(file)

parts = ['paragraph', 'sentence', 'page']
languages = ["en", "sk", "de"]
queries_by_language = {
    "en": en_queries,
    # "sk": sk_queries,
    # "de": de_queries
}


def search(part, query):
    db.execute("""
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
                ORDER BY
                    content <-> %s
            )
            GROUP BY
                document_id
        )
        ORDER BY
            similarity DESC,
            matches DESC,
            id ASC;
    """, (query, part, query, query))

    results = db.fetchall()
    return results


for part in parts[:1]:
    for lang in languages:
        queries = queries_by_language[lang]

        for query in queries[:10]:
            results = search(part, query)
            print(results)
