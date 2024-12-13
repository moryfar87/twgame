from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .. import crud, schemas
from ..database import get_db
from ..utils import create_access_token, verify_password, get_current_user
import secrets

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(f"Attempting login for user: {form_data.username}")
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user:
        print(f"User not found: {form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect email")

    print(f"User found: {user.email}")
    if not verify_password(form_data.password, user.password):
        print(f"Password verification failed for user: {user.email}")
        raise HTTPException(status_code=400, detail="Incorrect password")

    print(f"Password verified for user: {user.email}")

    access_token = create_access_token(data={"sub": user.email})

    client_id = secrets.token_urlsafe(16)
    client_secret = secrets.token_urlsafe(32)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "client_id": client_id,
        "client_secret": client_secret
    }


@router.post("/posts", response_model=schemas.PostResponse)
def create_post(
        post: schemas.PostCreate,
        db: Session = Depends(get_db),
        current_user: schemas.UserResponse = Depends(get_current_user)
):
    return crud.create_post(db=db, post=post, user_id=current_user.user_id)
