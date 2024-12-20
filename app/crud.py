from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from . import models, schemas
from .models import Post, User
from .schemas import PostCreate
from .utils import hash_password
from typing import List


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


def get_posts(db: Session, game: str = None, skip: int = 0, limit: int = 10):
    query = db.query(Post).join(User)
    if game:
        query = query.filter(Post.game == game)
    return query.options(joinedload(Post.user)).offset(skip).limit(limit).all()


def create_post(db: Session, post: PostCreate, user_id: int):
    db_post = Post(
        title=post.title,
        content_text=post.content_text,
        game=post.game,
        user_id=user_id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_posts(db: Session, skip: int = 0, limit: int = 10) -> List[models.Post]:
    return db.query(models.Post).order_by(models.Post.creation_date.desc()).offset(skip).limit(limit).all()


def get_post(db: Session, post_id: int):
    return db.query(models.Post).filter(models.Post.post_id == post_id).first()