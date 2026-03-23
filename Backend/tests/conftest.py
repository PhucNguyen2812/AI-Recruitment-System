# ============================================================
# tests/conftest.py
# Pytest configuration: in-memory SQLite DB + TestClient
# ============================================================
import pytest
import app.core.database as db_module
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db

# ── SQLite engine cho tests ─────────────────────────────────
import os
TEST_DB_PATH = "./test.db"
if os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

SQLALCHEMY_TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH}"

engine_test = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)



def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """
    FastAPI TestClient với SQLite in-memory DB.
    Patch module-level engine/SessionLocal trong app.core.database
    TRƯỚC khi lifespan chạy.
    """
    # Patch engine và SessionLocal trong module database
    original_engine = db_module.engine
    original_session = db_module.SessionLocal

    db_module.engine = engine_test
    db_module.SessionLocal = TestingSessionLocal

    from app.main import app
    app.dependency_overrides[get_db] = override_get_db

    # Tạo bảng với SQLite (đảm bảo models đã import)
    Base.metadata.create_all(bind=engine_test)

    from app.services.auth_service import seed_super_admin
    db = TestingSessionLocal()
    try:
        seed_super_admin(db)
    finally:
        db.close()

    with TestClient(app) as c:
        yield c

    # Cleanup
    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.clear()
    db_module.engine = original_engine
    db_module.SessionLocal = original_session


@pytest.fixture
def admin_token(client: TestClient) -> str:
    """Lấy JWT token của Super Admin."""
    from app.core.config import get_settings
    settings = get_settings()
    resp = client.post("/api/auth/login", json={
        "email": settings.SUPER_ADMIN_EMAIL,
        "mat_khau": settings.SUPER_ADMIN_PASSWORD,
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]

@pytest.fixture
def auth_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}

