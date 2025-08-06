# Initiate DB
from backend.models.umixin import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config.settings import settings


DATABASE_URL = settings.DATABASE_URL

# Base = declarative_base()
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.is_sqlite else {}
)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 每次 API 被呼叫時，FastAPI 會執行 get_db()，開啟一個 DB session。
# 路由中的參數 db: Session = Depends(get_db) 就會拿到這個 session。
# 執行完後自動關閉，確保資源釋放。
