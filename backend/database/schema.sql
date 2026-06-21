-- ==========================================
-- Extensions
-- ==========================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ==========================================
-- Providers
-- ==========================================

CREATE TABLE providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO providers (name)
VALUES
('groq'),
('gemini');

-- ==========================================
-- Route Prototypes
-- Cold-start router
-- ==========================================

CREATE TABLE route_prototypes (
    id SERIAL PRIMARY KEY,

    category VARCHAR(50) NOT NULL,

    example_prompt TEXT NOT NULL,

    provider_id INTEGER NOT NULL
        REFERENCES providers(id),

    embedding VECTOR(384) NOT NULL
);

-- ==========================================
-- Requests
-- Semantic cache source of truth
-- ==========================================

CREATE TABLE requests (
    id BIGSERIAL PRIMARY KEY,

    prompt TEXT NOT NULL,

    embedding VECTOR(384) NOT NULL,

    status VARCHAR(20) NOT NULL,

    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT request_status_check
    CHECK (
        status IN (
            'pending',
            'completed',
            'failed'
        )
    )
);

-- ==========================================
-- Responses
-- ==========================================

CREATE TABLE responses (
    id BIGSERIAL PRIMARY KEY,

    request_id BIGINT NOT NULL
        REFERENCES requests(id),

    provider_id INTEGER NOT NULL
        REFERENCES providers(id),

    content TEXT NOT NULL,

    latency_ms INTEGER,

    token_count INTEGER,

    estimated_cost DECIMAL(10,6),

    created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- Routing Decisions
-- ==========================================

CREATE TABLE routing_decisions (
    id BIGSERIAL PRIMARY KEY,

    request_id BIGINT NOT NULL
        REFERENCES requests(id),

    provider_id INTEGER NOT NULL
        REFERENCES providers(id),

    router_type VARCHAR(50) NOT NULL,

    confidence FLOAT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- Indexes
-- ==========================================

CREATE INDEX responses_request_idx
ON responses(request_id);

CREATE INDEX routing_request_idx
ON routing_decisions(request_id);

-- pgvector HNSW index
CREATE INDEX requests_embedding_idx
ON requests
USING hnsw (embedding vector_cosine_ops);