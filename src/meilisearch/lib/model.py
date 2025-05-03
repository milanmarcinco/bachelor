from sentence_transformers import SentenceTransformer
from typing import List

from lib.conf import ModelDetail


def get_detailed_instruct(prompt: str, query: str):
    return f"Instruct: {prompt}\nQuery: {query}"


class Model:
    def __init__(self, model: ModelDetail):
        self.model_name = model["model_name"]
        self.embedding_size = model["embedding_size"]
        self.query_prompt = model["query_prompt"]

        self.model = SentenceTransformer(
            self.model_name,
            trust_remote_code=True
        )

    def encode(self, passages: List[str]):
        instructed_passages = [get_detailed_instruct(self.query_prompt, passage) for passage in passages] \
            if self.query_prompt is not None else passages

        raw_embeddings = self.model.encode(
            instructed_passages,
            normalize_embeddings=True
        )

        embeddings: List[List[float]] = []

        for embedding in raw_embeddings:
            embeddings.append(
                embedding.tolist()
            )

        return embeddings
