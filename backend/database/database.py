from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:sitaram@localhost:5432/llm_gateway"

engine = create_engine(DATABASE_URL)