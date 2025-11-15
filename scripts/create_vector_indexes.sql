-- Create vector indexes for law and case embeddings
-- Run this script AFTER loading embeddings data into the database

-- This script should be run after embeddings have been generated
-- The IVFFlat index requires data to be present for training

-- For law embeddings
CREATE INDEX IF NOT EXISTS idx_law_embeddings_vector
ON law_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- For case embeddings
CREATE INDEX IF NOT EXISTS idx_case_embeddings_vector
ON case_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Alternatively, you can use HNSW index for better query performance
-- but it requires more memory and build time

-- CREATE INDEX idx_law_embeddings_hnsw
-- ON law_embeddings
-- USING hnsw (embedding vector_cosine_ops)
-- WITH (m = 16, ef_construction = 64);

-- CREATE INDEX idx_case_embeddings_hnsw
-- ON case_embeddings
-- USING hnsw (embedding vector_cosine_ops)
-- WITH (m = 16, ef_construction = 64);

-- Analyze tables for better query planning
ANALYZE law_embeddings;
ANALYZE case_embeddings;
