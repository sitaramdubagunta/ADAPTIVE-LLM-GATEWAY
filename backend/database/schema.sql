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
-- Users
-- ==========================================

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,

    email TEXT UNIQUE NOT NULL,

    password_hash TEXT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- User Provider Keys
-- Bring Your Own API Key
-- ==========================================

CREATE TABLE user_provider_keys (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES users(id),

    provider_id INTEGER NOT NULL
        REFERENCES providers(id),

    encrypted_api_key TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, provider_id)
);

-- ==========================================
-- Agents
-- Future Agent Support
-- ==========================================

CREATE TABLE agents (
    id BIGSERIAL PRIMARY KEY,

    name VARCHAR(100) UNIQUE NOT NULL,

    description TEXT,

    provider_id INTEGER
        REFERENCES providers(id),

    created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- Chats
-- ==========================================

CREATE TABLE chats (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES users(id),

    agent_id BIGINT
        REFERENCES agents(id),

    title TEXT,

    created_at TIMESTAMP DEFAULT NOW(),

    updated_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- Requests
-- User Messages
-- ==========================================

CREATE TABLE requests (
    id BIGSERIAL PRIMARY KEY,

    chat_id BIGINT NOT NULL
        REFERENCES chats(id),

    prompt TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT NOW()
);

-- ==========================================
-- Responses
-- LLM Outputs
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
-- Route Prototypes
-- Cold Start Router
-- ==========================================

CREATE TABLE route_prototypes (
    id BIGSERIAL PRIMARY KEY,

    category VARCHAR(50) NOT NULL,

    example_prompt TEXT NOT NULL,

    embedding VECTOR(384) NOT NULL,

    provider_id INTEGER NOT NULL
        REFERENCES providers(id)
);

-- ==========================================
-- Indexes
-- ==========================================

CREATE INDEX chats_user_idx
ON chats(user_id);

CREATE INDEX requests_chat_idx
ON requests(chat_id);

CREATE INDEX responses_request_idx
ON responses(request_id);

CREATE INDEX route_prototypes_embedding_idx
ON route_prototypes
USING hnsw (embedding vector_cosine_ops);