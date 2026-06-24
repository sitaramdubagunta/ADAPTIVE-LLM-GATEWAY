import os
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "llm-gateway-fallback-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
MAX_BCRYPT_PASSWORD_BYTES = 72


def _password_byte_length(password) -> int:
    return len(password.encode("utf-8"))


def verify_password(plain_password, hashed_password) -> bool:
    if _password_byte_length(plain_password) > MAX_BCRYPT_PASSWORD_BYTES:
        return False

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    if _password_byte_length(password) > MAX_BCRYPT_PASSWORD_BYTES:
        raise ValueError("Password must be 72 bytes or fewer after UTF-8 encoding.")

    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)