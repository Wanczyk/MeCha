from pydantic import BaseModel


class TokenBase(BaseModel):
    access_token: str
    token_type: str


class TokenCreate(TokenBase):
    pass


class Token(TokenBase):
    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    username: str
    disabled: bool = False
    bio: str | None = None


class UserCreate(UserBase):
    password: str


class UserProfile(UserBase):
    class Config:
        orm_mode = True


class User(UserBase):
    id: int
    token: Token

    class Config:
        orm_mode = True
