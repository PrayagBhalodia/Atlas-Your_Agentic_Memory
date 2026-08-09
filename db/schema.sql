-- ATLAS — Track A schema (decisions + memory_index)
-- Run once against the CockroachDB cluster:
--   cockroach sql --url "$COCKROACH_DATABASE_URL" -f db/schema.sql
-- or pipe it through psql / the smoke_test bootstrap.
--
-- VECTOR DIMENSION — READ THIS BEFORE CHANGING:
--   Embedding provider is Gemini `gemini-embedding-001` while AWS Bedrock is blocked.
--   Its native output is 3072 dims, BUT it supports Matryoshka truncation to 768/1536/3072
--   via output_dimensionality. We use 1536 on purpose:
--     - HNSW vector indexes have a per-dimension ceiling (pgvector caps at 2000; Cockroach
--       is in the same neighborhood), so 3072 risks an un-indexable column.
--     - 1536 keeps the HNSW index valid and is plenty for tag-level search.
--   THE RULE (TRACK_A §5.2): every embedding — stored tags AND incoming queries — must be
--   produced by the SAME model at the SAME dimension. If this number changes, ALL vectors
--   must be regenerated together. Keep it in sync with EMBED_DIM in db/config or the helper.

CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic STRING NOT NULL,
    old_state STRING,
    new_state STRING NOT NULL,
    cause STRING,
    trigger_event STRING,
    tension STRING,
    recorded_by STRING NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS memory_index (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic STRING NOT NULL,
    decision_id UUID REFERENCES decisions(id),
    tag STRING NOT NULL,
    tag_embedding VECTOR(1536),
    sequence_num INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS memory_index_hnsw
    ON memory_index USING HNSW (tag_embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS memory_index_topic_seq
    ON memory_index (topic, sequence_num);
