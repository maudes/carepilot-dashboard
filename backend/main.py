from fastapi import FastAPI
from dotenv import load_dotenv
import os
from backend.config.settings import settings

from .db import engine, get_db
from .models.umixin import Base
# import .routers all

# Read dotenv settings
env = os.getenv("ENV", "development")
load_dotenv(f".env.{env}")

# Create the FastAPI app instance
app = FastAPI(title="CarePilot API")


@app.get("/")
def health_check():
    return {"status": "ok", "message": f"FastAPI is running in {settings.env} 🎉"}


@app.get("/hello")
def say_hello(name: str = "world"):
    return {"greeting": f"Hello, {name}!"}

# app.include_router(user.router, prefix="/api", tags=["User Management"])  
# 為路由組添加前綴和標籤
