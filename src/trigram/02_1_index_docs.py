import json
from helpers.db import db
from helpers.helpers import now

with open("data/library/metadata.json", "r") as file:
    documents = json.load(file)

print(now(), "Inserting documents...", flush=True)

batch_size = 100
batches = [
    documents[i:i+batch_size]
    for i in range(0, len(documents), batch_size)
]

for batch in batches:
    sql = f"""
      INSERT INTO documents (id, title) VALUES
      {", ".join(["(%s, %s)"] * len(batch))};
    """

    parameters = []
    for document in batch:
        parameters.append(document["pk"])
        parameters.append(document["title"])

    db.execute(sql, parameters)

print(now(), "Done.", flush=True)
