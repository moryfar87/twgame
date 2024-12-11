from sqlalchemy.orm import Session
from . import models, schemas
from .utils import hash_password


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email, username=user.username, hashed_password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()
