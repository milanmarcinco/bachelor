import json
import uuid
import math
import random
from typing import List, Tuple
from numpy import ndarray

from lib.conf import Part, PARTS, MODEL_IDS, MODEL_DETAILS
from lib.meili import client, get_index_name
from lib.model import Model

index_name = get_index_name("paragraphs", "e5")
index = client.index(index_name)


results = index.search(None, {
    "limit": 10,
    "showRankingScore": True,
    "vector": [random.random() for _ in range(768)],
    "hybrid": {
        "embedder": "default",
        "semanticRatio": 1
    }
})

print(results)
