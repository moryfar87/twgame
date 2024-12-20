from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base
from sqlalchemy.orm import relationship
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(60), unique=True, nullable=False, index=True)
    email = Column(String(60), unique=True, nullable=False, index=True)
    password = Column(Text, nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    bio = Column(Text)

    posts = relationship("Post", back_populates="user")


class GameEnum(Enum):
    minecraft = "minecraft"
    fortnite = "fortnite"
    csgo = "csgo"
    lol = "lol"


class Post(Base):
    __tablename__ = "posts"

    post_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    title = Column(String(200), nullable=False)
    content_text = Column(Text, nullable=False)
    game = Column(SQLAlchemyEnum(GameEnum), nullable=False)
    creation_date = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="posts")
