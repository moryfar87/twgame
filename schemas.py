from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    
    model_config = ConfigDict(from_attributes=True)

class TokenData(BaseModel):
    username: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserBase):
    id: int
    hashed_password: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class MessageResponse(BaseModel):
    message: str
    
    model_config = ConfigDict(from_attributes=True)

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse
    
    model_config = ConfigDict(from_attributes=True)

class ProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProfileResponse(BaseModel):
    username: str
    email: EmailStr
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Дополнительные схемы для валидации
class PasswordReset(BaseModel):
    email: EmailStr
    
    model_config = ConfigDict(from_attributes=True)

class NewPassword(BaseModel):
    token: str
    new_password: str
    
    model_config = ConfigDict(from_attributes=True)

class EmailUpdate(BaseModel):
    new_email: EmailStr
    password: str
    
    model_config = ConfigDict(from_attributes=True)

class ValidationError(BaseModel):
    loc: list[str]
    msg: str
    type: str
    
    model_config = ConfigDict(from_attributes=True)

class HTTPError(BaseModel):
    detail: str
    
    model_config = ConfigDict(from_attributes=True)
