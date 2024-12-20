from typing import Annotated, List
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import JSONResponse, RedirectResponse

from app.schemas import UserCreate, UserResponse, PostResponse, PostCreate
from app.crud import get_user_by_email, create_user, get_posts, get_post
from app.crud import create_post as crud_create_post
from app.database import get_db
from app.utils import verify_password, get_current_user
from app.models import User
from app.schemas import LoginRequest, LoginResponse



router = APIRouter()
security = HTTPBasic()


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if not user.username or not user.email or not user.password:
            raise HTTPException(
                status_code=422,
                detail="All fields are required"
            )

        existing_user = get_user_by_email(db, email=user.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        created_user = create_user(db=db, user=user)
        return {"message": "User created successfully", "user_id": created_user.user_id}

    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.options("/register")
async def options_register():
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:8000",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=credentials.email)

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    return {"username": user.username}


@router.post("/posts", response_model=PostResponse)
def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_create_post(db=db, post=post, user_id=current_user.user_id)


@router.get("/posts", response_model=List[PostResponse])
def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    posts = get_posts(db, skip=skip, limit=limit)
    return posts


@router.get("/posts/{post_id}", response_model=PostResponse)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = get_post(db, post_id=post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post
