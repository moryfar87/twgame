from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Annotated
import jwt
from passlib.context import CryptContext
from . import models, schemas, database
from .database import get_db

app = FastAPI()

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройки безопасности
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Вспомогательные функции
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# Маршруты API
@app.post("/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверка существующего пользователя
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) | 
        (models.User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )

    # Создание нового пользователя
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
@app.post("/login", response_model=schemas.LoginResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    # Поиск пользователя
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Обновление времени последнего входа
    user.last_login = datetime.utcnow()
    db.commit()

    # Создание токена доступа
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/profile", response_model=schemas.ProfileResponse)
async def get_profile(
    current_user: Annotated[models.User, Depends(get_current_user)]
):
    return current_user

@app.put("/profile/update", response_model=schemas.ProfileResponse)
async def update_profile(
    profile_data: schemas.ProfileUpdate,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    # Проверка текущего пароля при обновлении
    if profile_data.new_password and not verify_password(
        profile_data.current_password, current_user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )

    # Обновление email
    if profile_data.email:
        # Проверка, не занят ли email другим пользователем
        existing_user = db.query(models.User).filter(
            models.User.email == profile_data.email
        ).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = profile_data.email

    # Обновление пароля
    if profile_data.new_password:
        current_user.password = get_password_hash(profile_data.new_password)

    db.commit()
    db.refresh(current_user)
    return current_user

@app.delete("/profile", response_model=schemas.MessageResponse)
async def delete_profile(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    db.delete(current_user)
    db.commit()
    return {"message": "Profile successfully deleted"}

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/password-reset", response_model=schemas.MessageResponse)
async def request_password_reset(
    email_data: schemas.PasswordReset,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email not found"
        )
    
    # Здесь можно добавить логику отправки email для сброса пароля
    return {"message": "Password reset instructions sent to email"}

@app.post("/password-reset/confirm", response_model=schemas.MessageResponse)
async def reset_password(
    password_data: schemas.NewPassword,
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(password_data.token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.password = get_password_hash(password_data.new_password)
    db.commit()
    return {"message": "Password successfully reset"}

@app.get("/users/me", response_model=schemas.UserResponse)
async def read_users_me(
    current_user: Annotated[models.User, Depends(get_current_user)]
):
    return current_user

@app.post("/email/verify", response_model=schemas.MessageResponse)
async def verify_email(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    # Здесь можно добавить логику верификации email
    return {"message": "Email verification link sent"}

# Обработчики ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "detail": exc.detail,
        "status_code": exc.status_code
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return {
        "detail": "Internal server error",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
    }
# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    models.Base.metadata.create_all(bind=database.engine)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
# Дополнительные эндпоинты

@app.get("/users/count", response_model=dict)
async def get_users_count(db: Session = Depends(get_db)):
    """Получить общее количество зарегистрированных пользователей"""
    count = db.query(models.User).count()
    return {"total_users": count}

@app.get("/users/online", response_model=dict)
async def get_online_users(db: Session = Depends(get_db)):
    """Получить количество пользователей, активных за последние 15 минут"""
    fifteen_minutes_ago = datetime.utcnow() - timedelta(minutes=15)
    online_count = db.query(models.User).filter(
        models.User.last_login >= fifteen_minutes_ago
    ).count()
    return {"online_users": online_count}

@app.post("/profile/avatar", response_model=schemas.MessageResponse)
async def update_avatar(
    file: UploadFile,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Session = Depends(get_db)
):
    """Обновить аватар пользователя"""
    try:
        # Здесь должна быть логика сохранения файла
        # и обновления ссылки на аватар в базе данных
        return {"message": "Avatar updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"Path: {request.url.path} "
        f"Method: {request.method} "
        f"Processing Time: {process_time:.4f}s "
        f"Status Code: {response.status_code}"
    )
    
    return response

# Настройка логирования
import logging
import time
from fastapi import Request

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Запуск приложения с дополнительными настройками
if __name__ == "__main__":
    import uvicorn
    
    # Создание таблиц в базе данных
    models.Base.metadata.create_all(bind=database.engine)
    
    # Настройки uvicorn
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4,
        log_level="info",
        access_log=True,
        use_colors=True
    )
    
    server = uvicorn.Server(config)
    
    try:
        logger.info("Starting server...")
        server.run()
    except
    try:
        logger.info("Starting server...")
        server.run()
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        logger.info("Shutting down server...")
        # Закрытие соединений с базой данных
        database.SessionLocal.close_all()

# Добавим конфигурацию для разных окружений
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI User Management"
    DEBUG: bool = False
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./users.db"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()

# Обновим конфигурацию приложения
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version=settings.VERSION,
    description="User management API with authentication and profile management",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)


# Добавим документацию к API
tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users",
    },
    {
        "name": "auth",
        "description": "Authentication operations",
    },
    {
        "name": "profile",
        "description": "Profile management",
    },
]

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version=settings.VERSION,
    openapi_tags=tags_metadata
)

# Добавим rate limiting
from fastapi_limiter import FastAPILimiter
import aioredis

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)

# Применим rate limiting к эндпоинтам
from fastapi_limiter.depends import RateLimiter

@app.post("/login", dependencies=[Depends(RateLimiter(times=5, minutes=1))])
async def login():
    pass

# Добавим кэширование
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

@app.get("/users/count", response_model=dict)
@cache(expire=60)
async def get_users_count():
    pass


