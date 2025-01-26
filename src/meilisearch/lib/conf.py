import dotenv
from typing import List, Dict, Literal, TypedDict

Part = Literal["sentences", "paragraphs", "pages"]
ModelId = Literal["e5", "labse", "gte"]


class ModelDetail(TypedDict):
    model_name: str
    embedding_size: int


env = dotenv.dotenv_values()


MEILI_KEY: str = env["MEILI_KEY"]
MEILI_URL: str = env["MEILI_URL"]

PARTS: List[Part] = ["paragraphs", "sentences", "pages"][:1]
MODEL_IDS: List[ModelId] = ["e5", "labse", "gte"]

MODEL_DETAILS: Dict[ModelId, ModelDetail] = {
    "e5": {
        "model_name": "intfloat/multilingual-e5-large-instruct",
        "embedding_size": 1024
    },
    "labse": {
        "model_name": "sentence-transformers/LaBSE",
        "embedding_size": 768
    },
    "gte": {
        "model_name": "Alibaba-NLP/gte-multilingual-base",
        "embedding_size": 768
    }
}
