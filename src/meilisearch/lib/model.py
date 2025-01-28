from lib.conf import ModelDetail
from typing import List
from sentence_transformers import SentenceTransformer


class Model:
    def __init__(self, model: ModelDetail):
        self.model_name = model["model_name"]
        self.embedding_size = model["embedding_size"]

        self.model = SentenceTransformer(
            self.model_name,
            trust_remote_code=True
        )

    def encode(self, parts: List[str]):
        return self.model.encode(
            parts,
            normalize_embeddings=True
        )
