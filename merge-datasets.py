import json

f1 = open('dataset/_entities-1.json')
f2 = open('dataset/_entities-2.json')

collection_1 = json.load(f1)
collection_2 = json.load(f2)

merged = collection_1 + collection_2

# authors = {}
# author_mappings = {}
acquisition_mappings = {}
new_collection = []

# for entity in merged:
#   if entity['model'] == 'core.author':
#     entry_pk = entity['pk']
#     authors[entry_pk] = {
#       'name': entity['fields']['name'],
#       'surname': entity['fields']['surname'],
#     }

# for entity in merged:
#   if entity['model'] == 'core.entryauthor':
#     author_mappings[entity['fields']['entry']] = entity['fields']['author']

for entity in merged:
  if entity['model'] == 'core.acquisition':
    acquisition_mappings[entity['fields']['entry']] = entity['fields']['content']

for entity in merged:
  if entity['model'] == 'core.entry':
    entry_pk = entity['pk']
    # author_id = author_mappings[entry_pk] if entry_pk in author_mappings else None
    # author = authors[author_id] if author_id in authors else None

    if entry_pk in acquisition_mappings:
      pdf_path = acquisition_mappings[entry_pk]
      pdf_name = pdf_path.split('/')[-1]
      pk = pdf_name.split('.')[0]

    new_collection.append({
      "pk": pk,
      "filename": pdf_name,
      "title": entity['fields']['title'],
      # "author": {
      #   "name": author['name'],
      #   "surname": author['surname'],
      # } if author else None
    })

f1.close()
f2.close()

with open('dataset/_merged.json', 'w') as f:
  json.dump(new_collection, f, indent=2)
