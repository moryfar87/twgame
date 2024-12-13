from sqlalchemy import select
from sqlalchemy.orm import Session
from . import models, schemas
from .utils import hash_password


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_post(db: Session, post: schemas.PostCreate, user_id: int):
    db_post = models.Post(
        content_text=post.content_text,
        user_id=user_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post
