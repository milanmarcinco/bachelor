def decode(encoded_string):
    return encoded_string.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')

with open("01_results.json", "r") as f:
    documents = json.load(f)

new_documents = []
for doc in documents:
    new_documents.append({
        "id": doc["id"],
        "title": decode(doc["title"]),
        "summary": decode(doc["summary"])
    })

documents_str = json.dumps(
    new_documents,
    indent=2,
    ensure_ascii=False
)

print(documents_str)
