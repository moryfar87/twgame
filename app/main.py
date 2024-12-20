from fastapi import FastAPI
from app.api.auth import router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_path = os.path.join(BASE_DIR, 'front', 'static')
index_path = os.path.join(BASE_DIR, 'front', 'index.html')

app.mount("/static", StaticFiles(directory=static_path), name="static")

if not os.path.exists(static_path):
    raise RuntimeError(f"Directory '{static_path}' does not exist")


@app.get("/")
async def read_index():
    index_path = os.path.join(static_path, "index.html")
    if not os.path.exists(index_path):
        raise RuntimeError(f"File '{index_path}' does not exist")
    return FileResponse(index_path)


