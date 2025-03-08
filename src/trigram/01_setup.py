from helpers.db import db

print("Setting up database...", flush=True)

db.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

db.execute("""
    CREATE TABLE documents (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        title VARCHAR(255) NOT NULL
    );

    CREATE TYPE PART AS ENUM (
        'page',
        'paragraph',
        'sentence'
    );
           
    CREATE TABLE document_parts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        document_id UUID NOT NULL REFERENCES documents(id),
        part PART NOT NULL,
        content TEXT NOT NULL
    );
""")

db.execute("""
    CREATE INDEX IF NOT EXISTS trgm_content_idx
    ON document_parts
    USING GIN (content gin_trgm_ops);
""")

db.execute("""
    CREATE INDEX IF NOT EXISTS part_idx
    ON document_parts
    USING HASH (part);
""")

db.execute("SET pg_trgm.similarity_threshold = 0;")

print("Set up finished...", flush=True)
