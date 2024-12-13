from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud, database

router = APIRouter()


# Открытие сессии БД для каждого запроса
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Получение информации о пользователе по ID
@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Обновление данных пользователя
@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Здесь можно добавить логику для обновления данных пользователя
    db_user.username = user.username
    db_user.email = user.email
    # Не обновляем пароль напрямую (будет отдельно обработка пароля)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
