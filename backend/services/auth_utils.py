# auth_utils.py
import os
from datetime import datetime, timedelta, timezone
import jwt
import bcrypt  # <-- Import native bcrypt instead of passlib

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "llm-gateway-fallback-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
MAX_BCRYPT_PASSWORD_BYTES = 72


def _password_byte_length(password) -> int:
    return len(password.encode("utf-8"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if _password_byte_length(plain_password) > MAX_BCRYPT_PASSWORD_BYTES:
        return False
    
    # native bcrypt requires bytes for both inputs
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    if _password_byte_length(password) > MAX_BCRYPT_PASSWORD_BYTES:
        raise ValueError("Password must be 72 bytes or fewer after UTF-8 encoding.")
    
    password_bytes = password.encode("utf-8")
    # Generating a salt and hashing
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    
    return hashed_bytes.decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)