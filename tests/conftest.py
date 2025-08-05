import sys
print("PYTHONPATH:", sys.path)
# Shared functions and fixtures for tests
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.umixin import Base
from backend.db import get_db
from fastapi.testclient import TestClient
from backend.main import app

# Use SQLite in-memory DB (Rebuild on each test run)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Build up test DB
Base.metadata.create_all(bind=engine)


# 替換 FastAPI 的 get_db 依賴
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    return TestClient(app)
