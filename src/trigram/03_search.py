import json
import os
from threading import Thread, Lock
from multiprocessing import Queue
from typing import List, Tuple, TypedDict, Callable
from psycopg2.extensions import connection

from helpers.db import connection_factory
from helpers.helpers import now


class Task(TypedDict):
    part: str
    lang: str
    query: str
    query_id: int


class Document(TypedDict):
    id: str
    similarity: float


class TaskResult(TypedDict):
    part: str
    lang: str
    query: str
    query_id: int
    documents: List[Document]


dirpath = f"data/retrieval/trigram"
os.makedirs(dirpath, exist_ok=True)

with open("data/dataset/02_queries-EN.json", "r") as file:
    en_queries: List[str] = json.load(file)
with open("data/dataset/02_queries-SK.json", "r") as file:
    sk_queries: List[str] = json.load(file)
with open("data/dataset/02_queries-DE.json", "r") as file:
    de_queries: List[str] = json.load(file)

parts = ['paragraph', 'sentence', 'page'][1:2]
threshold_by_unit = {
    "page": 0.12,
    "paragraph": 0.18,
    "sentence": 0.21
}

languages = ["en", "sk", "de"]
queries_by_language = {
    "en": en_queries,
    "sk": sk_queries,
    "de": de_queries
}


def search(connection: connection, part: str, query: str):
    threshold = threshold_by_unit[part]

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SET pg_trgm.similarity_threshold = %s;

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
        """, (threshold, query, part, query))

        results = cursor.fetchall()
        cursor.close()

        return results
    except:
        return None


print_lock = Lock()


def safe_print(*args, **kwargs):
    print_lock.acquire()
    print(f"{now()}", *args, **kwargs, flush=True)
    print_lock.release()


size = len(parts) * len(languages) * len(en_queries)
task_queue = Queue(size)
result_queue = Queue(size)

for part in parts:
    for lang in languages:
        queries = queries_by_language[lang]

        for idx, query in enumerate(queries):
            task_queue.put({
                "part": part,
                "lang": lang,
                "query": query,
                "query_id": idx + 1
            })


def process_tasks(idx: int, task_queue: Queue, result_queue: Queue, log: Callable):
    connection = connection_factory()

    while True:
        try:
            task: Task = task_queue.get_nowait()
        except:
            break

        task_id = f"{task['part']}-{task['lang']}-{task['query_id']}"
        log(f"Thread[{idx+1}]: Starting {task_id}")

        result: List[Tuple[str, float]] | None = search(
            connection,
            task["part"],
            task["query"]
        )

        if result is None:
            log(f"! Thread[{idx+1}]: Failed {task_id}")

        documents: List[Document] = [
            {
                "id": id,
                "similarity": similarity
            } for id, similarity in result
        ]

        task_result: TaskResult = {
            "part": task["part"],
            "lang": task["lang"],
            "query": task["query"],
            "query_id": task["query_id"],
            "documents": documents
        }

        result_queue.put(task_result)

        log(f"Thread[{idx+1}]: Finished {task_id}")

    connection.close()


def process_results(result_queue: Queue, log: Callable):
    while True:
        task_result: TaskResult | None = result_queue.get()

        if task_result is None:
            break

        part, lang, query_id = (
            task_result["part"],
            task_result["lang"],
            task_result["query_id"]
        )

        filepath = f"{dirpath}/{part}-{lang}-{query_id}.json"
        with open(filepath, "w") as file:
            json.dump(task_result, file, indent=2, ensure_ascii=False)

        task_id = f"{part}-{lang}-{query_id}"
        log(f"Saved {task_id}")


worker_threads: List[Thread] = []

for idx in range(8):
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
