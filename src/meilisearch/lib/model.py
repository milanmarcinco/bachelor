from numpy import ndarray
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

from lib.conf import ModelDetail


class Model:
    def __init__(self, model: ModelDetail):
        self.model_name = model["model_name"]
        self.embedding_size = model["embedding_size"]

        self.model = SentenceTransformer(
            self.model_name,
            trust_remote_code=True
        )

    def encode(self, parts: List[str]):
        raw_embeddings: List[
            ndarray[int, float]
        ] = self.model.encode(
            parts,
            normalize_embeddings=True
        )

        embeddings: List[List[float]] = []

        for embedding in raw_embeddings:
            embeddings.append(
                embedding.tolist()
            )

        return embeddings
