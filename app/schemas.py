from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


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


class Token(BaseModel):
    access_token: str
    token_type: str


class PostCreate(BaseModel):
    content_text: str


class Token(BaseModel):
    access_token: str
    token_type: str
    client_id: str
    client_secret: str


class PostResponse(PostCreate):
    post_id: int
    user_id: int
    creation_date: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    username: str
