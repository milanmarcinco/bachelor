import dotenv
from typing import List, Dict, Literal, TypedDict, Union

Part = Literal["sentence", "paragraph", "page"]
Language = Literal["en", "sk", "de"]
ModelId = Literal["e5", "labse", "gte"]


class ModelDetail(TypedDict):
    model_name: str
    embedding_size: int
    query_prompt: Union[str, None]


env = dotenv.dotenv_values()


MEILI_KEY: str = env["MEILI_KEY"]
MEILI_URL: str = env["MEILI_URL"]

PARTS: List[Part] = ["paragraph", "sentence", "page"]
LANGUAGES: List[Language] = ["en", "sk", "de"]
MODEL_IDS: List[ModelId] = ["e5", "labse", "gte"]

MODEL_DETAILS: Dict[ModelId, ModelDetail] = {
    "e5": {
        "model_name": "intfloat/multilingual-e5-large-instruct",
        "embedding_size": 1024,
        "query_prompt": "Given a search query, retrieve the most relevant passage.",
    },
    "labse": {
        "model_name": "sentence-transformers/LaBSE",
        "embedding_size": 768,
        "query_prompt": None,
    },
    "gte": {
        "model_name": "Alibaba-NLP/gte-multilingual-base",
        "embedding_size": 768,
        "query_prompt": None,
    }
}
