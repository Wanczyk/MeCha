from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.core.database import engine
from src.core.dependencies import get_db
from src.crud import user as user_crud
from src.schemas import user as user_schema
from src.models import user as user_model


router = APIRouter(prefix='/users', tags=["items"],)


user_model.Base.metadata.create_all(bind=engine)


@router.post("/register", response_model=user_schema.TokenBase)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = user_crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user_crud.create_user_and_return_token(db=db, user=user)


@router.post("/login", response_model=user_schema.TokenBase)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = user_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_crud.get_user_token(db, user)


@router.get("/me/", response_model=user_schema.UserProfile)
async def read_users_me(
    current_user: user_schema.UserProfile = Depends(user_crud.get_current_active_user)
):
    return current_user
