from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.crud.auth import auth
from src.models import user as user_model

from src.core.dependencies import get_db, oauth2_scheme

from src.schemas import user as user_schema


def get_current_user(
        db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    auth.validate_token(token)
    username = auth.get_username_from_token(token)
    return get_user_by_username(db, username)


def get_current_active_user(current_user: user_schema.User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive models")
    return current_user


def get_user_by_username(db: Session, username: str):
    return db.query(user_model.User).filter(user_model.User.username == username).first()


def authenticate_user(db, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not auth.verify_password(password, user.hashed_password):
        return False
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(user_model.User).filter(user_model.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(user_model.User).offset(skip).limit(limit).all()


def _update_user_token(token: str, db: Session, user: user_schema):
    user_token = db.query(user_model.Token).filter(user_model.Token.user_id == user.id).first()
    user_token.token = token
    db.commit()
    db.refresh(user_token)


def get_user_token(db: Session, user: user_schema.User):
    try:
        auth.validate_token(user.token.access_token)
        token = user.token
    except HTTPException:
        token = auth.create_access_token(data={"sub": user.username})
        _update_user_token(token, db, user)
    return {"access_token": token.access_token, "token_type": token.token_type}


def create_user_and_return_token(db: Session, user: user_schema.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = user_model.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token = auth.create_access_token(data={"sub": user.username})
    auth.create_token(token, db, db_user.id)
    return {"access_token": token, "token_type": "bearer"}
