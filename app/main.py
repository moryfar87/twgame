from fastapi import FastAPI
from app.api import auth

app = FastAPI()

# Регистрация маршрутов
app.include_router(auth.router)
