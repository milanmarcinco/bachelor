import requests
from lib.conf import PARTS, MODEL_IDS, MODEL_DETAILS, MEILI_URL, MEILI_KEY
from lib.meili import client, get_index_name

base_headers = {
    "Authorization": f"Bearer {MEILI_KEY}",
    "Content-Type": "application/json"
}


version = client.get_version()
print(f"MeiliSearch version: {version}")


res = requests.patch(
    f"{MEILI_URL}/experimental-features",
    json={"vectorStore": True},
    headers=base_headers
).json()


for model_id in MODEL_IDS:
    model_detail = MODEL_DETAILS[model_id]

    for part in PARTS:
        index_name = get_index_name(part, model_id)

        client.create_index(index_name)
        index = client.index(index_name)

        index.update_distinct_attribute("document_id")

        index.update_embedders({
            "default": {
                "source": "userProvided",
                "dimensions": model_detail["embedding_size"]
            }
        })
