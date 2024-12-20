from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    user_id: int
    registration_date: datetime
    bio: Optional[str] = None

    class Config:
        from_attributes = True



class PostBase(BaseModel):
    content_text: str


class GameEnum(str, Enum):
    minecraft = "minecraft"
    fortnite = "fortnite"
    csgo = "csgo"
    lol = "lol"


class PostCreate(BaseModel):
    title: str
    content_text: str
    game: GameEnum


class UserInfo(BaseModel):
    username: str

class PostResponse(BaseModel):
    post_id: int
    title: str
    content_text: str
    game: str
    creation_date: datetime
    user: UserInfo

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    username: str
