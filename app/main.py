from fastapi import FastAPI
from twgame.app.api.auth import router

app = FastAPI()

# Регистрация маршрутов
app.include_router(router)
