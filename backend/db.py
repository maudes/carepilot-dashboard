# Initiate DB
from backend.models.umixin import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config.settings import settings


DATABASE_URL = settings.DATABASE_URL

# Base = declarative_base()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.is_sqlite else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
