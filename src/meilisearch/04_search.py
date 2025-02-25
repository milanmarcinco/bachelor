import os
import json
from typing import List, TypedDict, Callable
from multiprocessing import Queue
from threading import Thread, Lock
from typing import List

from lib.conf import Part, ModelId, PARTS, LANGUAGES, MODEL_IDS, MODEL_DETAILS
from lib.meili import get_meilisearch_client, get_index_name
from lib.model import Model

N_THREADS = 4


class Task(TypedDict):
    task_id: str
    part: Part
    lang: str
    model_id: ModelId
    query: str
    query_id: int
    vector: List[float]


class Document(TypedDict):
    id: str
    similarity: float


class TaskResult(TypedDict):
    task_id: str
    part: Part
    lang: str
    model_id: ModelId
    query: str
    query_id: int
    documents: List[Document]


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


print_lock = Lock()


def safe_print(*args, **kwargs):
    print_lock.acquire()
    print(*args, **kwargs, flush=True)
    print_lock.release()


size = len(MODEL_IDS) * len(PARTS) * len(LANGUAGES) * len(en_queries)
task_queue = Queue(size)
result_queue = Queue(size)

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

                task_queue.put({
                    "task_id": task_id,
                    "part": part,
                    "lang": lang,
                    "model_id": model_id,
                    "query": query,
                    "query_id": query_id,
                    "vector": vector
                })


def process_tasks(idx: int, task_queue: Queue, result_queue: Queue, log: Callable):
    client = get_meilisearch_client()

    while True:
        try:
            task: Task = task_queue.get_nowait()
        except:
            break

        task_id, part, lang, model_id, query, query_id, vector = [
            task["task_id"],
            task["part"],
            task["lang"],
            task["model_id"],
            task["query"],
            task["query_id"],
            task["vector"]
        ]

        log(f"Thread[{idx+1}]: Starting {task_id}")

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

        documents: List[Document] = [
            {
                "id": document["document_id"],
                "similarity": document["_rankingScore"]
            }
            for document in response["hits"]
        ]

        task_result: TaskResult = {
            "task_id": task_id,
            "part": part,
            "lang": lang,
            "query": query,
            "model_id": model_id,
            "query_id": query_id,
            "documents": documents
        }

        result_queue.put(task_result)
        log(f"Thread[{idx+1}]: Finished {task_id}")


def process_results(result_queue: Queue, log: Callable):
    while True:
        task_result: TaskResult | None = result_queue.get()

        if task_result is None:
            break

        task_id, model_id = (
            task_result["task_id"],
            task_result["model_id"]
        )

        dirpath = f"{base_dirpath}/{model_id}"
        filepath = f"{dirpath}/{task_id}.json"
        with open(filepath, "w") as file:
            json.dump(task_result, file, indent=2, ensure_ascii=False)

        log(f"Saved {task_id}")


worker_threads: List[Thread] = []

for idx in range(N_THREADS):
    thread = Thread(
        target=process_tasks,
        args=(
            idx,
            task_queue,
            result_queue,
            safe_print
        )
    )

    worker_threads.append(thread)

result_thread = Thread(
    target=process_results,
    args=(result_queue, safe_print)
)

result_thread.start()

for thread in worker_threads:
    thread.start()

for thread in worker_threads:
    thread.join()

result_queue.put(None)
result_thread.join()
