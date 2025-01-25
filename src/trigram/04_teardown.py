from helpers.db import db

db.execute("DROP INDEX IF EXISTS trgm_content_idx")
db.execute("DROP INDEX IF EXISTS part_idx")
db.execute("DROP TABLE IF EXISTS documents CASCADE")
db.execute("DROP TABLE IF EXISTS document_parts CASCADE")
db.execute("DROP TYPE IF EXISTS PART CASCADE")
