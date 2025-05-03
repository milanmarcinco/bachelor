import json
from lib.conf import ROOT_PATH, DATA_DIR, UNITS

# Collection

with open(f"{DATA_DIR}/library/metadata.json", "r") as file:
    documents = json.load(file)

for unit in UNITS:
    collection_file = open(f"{ROOT_PATH}/{unit}s_collection.tsv", "w")
    mappings = {}
    i = 0

    for document in documents:
        id = document["pk"]

        with open(f"{DATA_DIR}/document_parts/json/{id}.json", "r") as file:
            parts = json.load(file)

        for part in parts[f"{unit}s"]:
            text = part.replace("\n", " ").replace("\t", " ")
            collection_file.write(f"{i}\t{text}\n")
            mappings[i] = id
            i += 1

    collection_file.close()

    with open(f"{ROOT_PATH}/{unit}s_mapping.json", "w") as mappings_file:
        json.dump(mappings, mappings_file, indent=2)


# Queries

query_files = {
    "en": "02_queries-EN.json",
    "de": "02_queries-DE.json",
    "sk": "02_queries-SK.json",
}

for lang, query_file_name in query_files.items():
    queries_file = open(f"{ROOT_PATH}/queries_{lang}.tsv", "w")

    with open(f"{DATA_DIR}/dataset/{query_file_name}", "r") as file:
        queries = json.load(file)

        for idx, query in enumerate(queries):
            queries_file.write(f"{idx}\t{query}")

            if idx < len(queries) - 1:
                queries_file.write("\n")

    queries_file.close()
