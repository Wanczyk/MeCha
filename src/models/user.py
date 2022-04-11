from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    bio = Column(String, nullable=True)

    token = relationship("Token", back_populates="user", uselist=False)


class Token(Base):
    __tablename__ = 'token'

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String)
    token_type = Column(String, default="bearer")
    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship('User', back_populates='token')
