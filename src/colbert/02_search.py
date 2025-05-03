import json

from colbert.data import Queries
from colbert.infra import Run, RunConfig, ColBERTConfig
from colbert import Searcher

from lib.conf import ROOT_PATH, EXPERIMENT, ROOT_PATH, LANGUAGES, UNITS, K
from lib.helpers import now

if __name__ == '__main__':
    for unit in UNITS:
        print(now(), "Search started")

        with open(f"{ROOT_PATH}/{unit}s_mapping.json", "r") as mappings_file:
            mappings = json.load(mappings)

        for lang in LANGUAGES:
            queries_file = f"{ROOT_PATH}/queries_{lang}.tsv"

            documents = {}
            metas = {}

            with Run().context(RunConfig(nranks=1, experiment=EXPERIMENT)):
                config = ColBERTConfig(
                    root=ROOT_PATH
                )

                index_name = f"{unit}_index"

                searcher = Searcher(index=index_name, config=config)
                queries = Queries(queries_file)
                ranking = searcher.search_all(queries, k=K)

                for item in ranking.tolist():
                    query_id, doc_id, rank, similarity = item
                    query_id += 1

                    real_doc_id = mappings[doc_id]

                    doc = {
                        "id": real_doc_id,
                        "similarity": similarity,
                    }

                    meta = {
                        "task_id": f"{unit}-{lang}-{query_id}",
                        "query_id": query_id,
                        "lang": lang,
                        "part": unit
                    }

                    metas[query_id] = meta

                    if query_id not in documents:
                        documents[query_id] = [doc]
                    else:
                        documents[query_id].append(doc)

            for query_id, meta in metas.items():
                dirpath = "../../data/retrieval/colbert/"
                filepath = f"{dirpath}/{unit}-{lang}-{query_id}.json"

                result = {
                    **meta,
                    "documents": documents[query_id]
                }

                with open(filepath, "w") as file:
                    json.dump(result, file, indent=2, ensure_ascii=False)

        print(now(), "Search finished")
