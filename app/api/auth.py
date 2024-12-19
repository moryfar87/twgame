from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from .. import crud, schemas
from ..database import get_db
from ..utils import verify_password, get_current_user
import secrets
from ..models import User
from ..schemas import LoginRequest, LoginResponse

router = APIRouter()
security = HTTPBasic()


@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=credentials.email)

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    return {"username": user.username}


@router.post("/posts", response_model=schemas.PostResponse)
def create_post(
        post: schemas.PostCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud.create_post(db=db, post=post, user_id=current_user.user_id)
    # return {"token_type": "basic"}
