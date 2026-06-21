from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:postgres@localhost:5433/llm_gateway"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)