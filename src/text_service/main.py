import json
import os
from multiprocessing import Process, Queue
from text_handler.TextService import TextHandler


def perform(idx: int, docs: Queue):
    log_file = open(f"output/logs_{idx}.txt", "w")

    while True:
        try:
            doc = docs.get_nowait()
        except:
            break

        id, filename = doc["pk"], doc["filename"]
        filepath = f"../../dataset/{filename}"

        log_file.write(f"[{id}]: Starting...\n")
        log_file.flush()

        try:
            text_handler = TextHandler(filepath)
            sentences, paragraphs, pages = text_handler.extract_text()
        except:
            sentences, paragraphs, pages = None, None, None

        with open(f"output/{id}.json", "w") as file:
            output = {
                "sentences": sentences,
                "paragraphs": paragraphs,
                "pages": pages
            }

            json.dump(
                output,
                file,
                indent=2,
                ensure_ascii=False
            )

        if all([
            type(sentences) == list,
            type(paragraphs) == list,
            type(pages) == list
        ]):
            a, b, c = len(sentences), len(paragraphs), len(pages)
            log_file.write(f"[{id}]: {a} {b} {c}\n")
        else:
            log_file.write(f"[{id}]: Failed\n")

        log_file.flush()


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)

    with open("../../dataset/merged.json", "r") as file:
        documents = json.load(file)

    docs = Queue(maxsize=len(documents))

    for document in documents:
        docs.put(document)

    processes = [
        Process(
            target=perform,
            args=(idx, docs),
            daemon=True
        )
        for idx in range(4)
    ]

    for process in processes:
        process.start()

    for process in processes:
        process.join()
