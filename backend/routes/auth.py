
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import re
import unicodedata

from database.models import User
from database.session import get_db
from services.auth_utils import create_access_token, get_password_hash, verify_password


router = APIRouter(prefix="/v1/auth", tags=["auth"])


def normalize_email(email: str) -> str:
    """Normalizes Unicode characters, strips padding, and lowercases the address."""
    clean_email = email.strip().lower()
    return unicodedata.normalize("NFKC", clean_email)


class UserCreate(BaseModel):
    email: EmailStr
    # Framework-level validation for minimum length
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Enforces strong password rules before hitting hashing functions."""
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
            
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")
            
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number.")
            
        if not re.search(r"[ !@#$%^&*(),.?\":{}|<>_+\-\[\]\\]", value):
            raise ValueError("Password must contain at least one special character.")
            
        return value


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    # Standardize email representation across systems
    email = normalize_email(payload.email)

    # Fast check using database indexes via unique id lookups
    if db.query(User.id).filter(User.email == email).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    try:
        password_hash = get_password_hash(payload.password)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    user = User(
        email=email,
        password_hash=password_hash,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Verify if the constraint failure was definitively a duplicate email collision
        if db.query(User.id).filter(User.email == email).first() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected database error occurred."
        )

    db.refresh(user)
    return user


@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Process incoming token parameters against identical normalization constraints
    email = normalize_email(form_data.username)
    user = db.query(User).filter(User.email == email).first()

    if user is None or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "id": user.id,
            "email": user.email,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }