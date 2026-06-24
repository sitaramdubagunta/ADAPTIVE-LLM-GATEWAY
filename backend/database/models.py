from sqlalchemy import BigInteger, Column, String, TIMESTAMP, text
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=text("NOW()"))