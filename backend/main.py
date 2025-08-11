from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Read dotenv settings
env = os.getenv("ENV", "development")
load_dotenv(f".env.{env}")

from backend.config.settings import settings
from .db import engine, get_db
from .models.umixin import Base
# from backend.routers import auth
# import .routers all
# Create the FastAPI app instance
app = FastAPI(
    title="CarePilot API",
    description="Maude's FastAPI/ Health side project.",
    version="0.1.0",
)

"""
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)
"""
# app.include_router(user.router, prefix="/api", tags=["User Management"])
# 為路由組添加前綴和標籤


@app.get("/")
def health_check():
    return {"status": "ok", "message": f"FastAPI is running in {settings.env} 🎉"}


@app.get("/hello")
def say_hello(name: str = "world"):
    return {"greeting": f"Hello, {name}!"}
