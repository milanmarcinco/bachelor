import meilisearch
from lib.conf import MEILI_URL, MEILI_KEY, Part, ModelId


def get_meilisearch_client():
    return meilisearch.Client(MEILI_URL, MEILI_KEY)


client = get_meilisearch_client()


def get_index_name(part: Part, model_id: ModelId):
    return f"{part}-{model_id}"
