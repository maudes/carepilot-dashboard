# import sys
# print("PYTHONPATH:", sys.path)
# Shared functions and fixtures for tests
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.models.umixin import Base
from backend.db import get_db
from fastapi.testclient import TestClient
from backend.main import app
from backend.redis_client import get_redis_client
from backend.models.user import Goal, User
from backend.routers.auth import get_current_user
from uuid import uuid4

# Use SQLite in-memory DB (Rebuild on each test run) & build connection/session
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # One shared connection, so the TestClient's thread sees the same
    # in-memory database as the fixtures
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

# Build up test DB (metadata)
Base.metadata.create_all(bind=engine)


# Replace FastAPI `get_db` dependency
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

# TsetClient: mimics HTTP requests to FastAPI app


@pytest.fixture()
def auth_client(client):
    """TestClient logged in as a throwaway user.

    Overrides `get_current_user`, so no token or Redis is needed.
    """
    db = TestingSessionLocal()
    user = User(email=f"{uuid4()}@test.com", is_verified=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        yield client
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        db.query(Goal).filter(Goal.user_id == user.id).delete()
        db.delete(user)
        db.commit()
        db.close()


@pytest.fixture(scope="session")
def redis_client():
    client = get_redis_client()
    return client
