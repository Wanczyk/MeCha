from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from src.core.dependencies import get_db
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.models import user as user_model
from src.core import settings
from src.core.exceptions import credentials_exception
from src.schemas import user as user_schema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict):
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def get_username_from_token(token: str):
    payload = _decode_token(token)
    return payload.get("sub")


def create_token(token: str, db: Session, user_id: int):
    db_token = user_model.Token(
        user_id=user_id,
        access_token=token,
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)


def _decode_token(token: str):
    return jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def validate_token(token: str):
    try:
        payload = _decode_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
