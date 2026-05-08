-- FEAT-014: pgvector schema for compliance documents
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS compliance_documents (
    id SERIAL PRIMARY KEY,
    municipality VARCHAR(255) NOT NULL,
    ordinance_text TEXT NOT NULL,
    embedding vector(768) -- assuming 768 dimensions for text embeddings
);

CREATE INDEX ON compliance_documents USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- RLS and Role for RAG endpoint (BUG-006)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'rag_readonly') THEN
    CREATE ROLE rag_readonly WITH NOLOGIN;
  END IF;
END
$$;

GRANT SELECT ON compliance_documents TO rag_readonly;

ALTER TABLE compliance_documents ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS rag_readonly_select_policy ON compliance_documents;
CREATE POLICY rag_readonly_select_policy 
    ON compliance_documents 
    FOR SELECT 
    TO rag_readonly 
    USING (true);
