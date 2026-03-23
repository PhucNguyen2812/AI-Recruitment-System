# ============================================================
# app/core/database.py
# SQLAlchemy engine + session factory + Base + dependency
# ============================================================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # tự kiểm tra connection trước mỗi query
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# ── FastAPI Dependency ────────────────────────────────────
def get_db():
    """Dependency injection: cung cấp DB session cho mỗi request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
