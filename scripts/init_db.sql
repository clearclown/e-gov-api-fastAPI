-- Database initialization script for e-gov Legal API
-- This script sets up the database schema with pgvector support

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Laws table (Phase 1)
CREATE TABLE IF NOT EXISTS laws (
    law_id VARCHAR(50) PRIMARY KEY,
    law_number VARCHAR(100) NOT NULL,
    law_name VARCHAR(500) NOT NULL,
    promulgation_date DATE,
    enforcement_date DATE,
    category VARCHAR(100),
    full_text TEXT NOT NULL,
    toc TEXT,
    appendix TEXT,
    last_updated DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cases table (Phase 2)
CREATE TABLE IF NOT EXISTS cases (
    case_id VARCHAR(50) PRIMARY KEY,
    case_number VARCHAR(100) NOT NULL,
    case_name VARCHAR(500) NOT NULL,
    court_name VARCHAR(200) NOT NULL,
    decision_date DATE NOT NULL,
    case_type VARCHAR(50),
    summary TEXT NOT NULL,
    holdings TEXT,
    case_summary TEXT,
    main_text TEXT NOT NULL,
    cited_laws TEXT[],
    related_cases TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Law embeddings table (Phase 3)
CREATE TABLE IF NOT EXISTS law_embeddings (
    id SERIAL PRIMARY KEY,
    law_id VARCHAR(50) NOT NULL REFERENCES laws(law_id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(law_id, chunk_index)
);

-- Case embeddings table (Phase 3)
CREATE TABLE IF NOT EXISTS case_embeddings (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(50) NOT NULL REFERENCES cases(case_id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(case_id, chunk_index)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_laws_law_number ON laws(law_number);
CREATE INDEX IF NOT EXISTS idx_laws_law_name ON laws(law_name);
CREATE INDEX IF NOT EXISTS idx_laws_category ON laws(category);
CREATE INDEX IF NOT EXISTS idx_laws_promulgation_date ON laws(promulgation_date);

CREATE INDEX IF NOT EXISTS idx_cases_case_number ON cases(case_number);
CREATE INDEX IF NOT EXISTS idx_cases_case_name ON cases(case_name);
CREATE INDEX IF NOT EXISTS idx_cases_court_name ON cases(court_name);
CREATE INDEX IF NOT EXISTS idx_cases_decision_date ON cases(decision_date);
CREATE INDEX IF NOT EXISTS idx_cases_case_type ON cases(case_type);

-- Create vector search indexes using IVFFlat algorithm
-- Note: These indexes should be created after data is loaded
-- CREATE INDEX ON law_embeddings USING ivfflat (embedding vector_cosine_ops)
-- WITH (lists = 100);

-- CREATE INDEX ON case_embeddings USING ivfflat (embedding vector_cosine_ops)
-- WITH (lists = 100);

-- Full-text search support (optional)
-- ALTER TABLE laws ADD COLUMN search_vector tsvector;
-- CREATE INDEX idx_laws_search ON laws USING gin(search_vector);

-- ALTER TABLE cases ADD COLUMN search_vector tsvector;
-- CREATE INDEX idx_cases_search ON cases USING gin(search_vector);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_laws_updated_at BEFORE UPDATE ON laws
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cases_updated_at BEFORE UPDATE ON cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE laws IS '日本の法令情報を格納するテーブル';
COMMENT ON TABLE cases IS '判例情報を格納するテーブル';
COMMENT ON TABLE law_embeddings IS '法令のベクトル埋め込みを格納するテーブル（RAG用）';
COMMENT ON TABLE case_embeddings IS '判例のベクトル埋め込みを格納するテーブル（RAG用）';
