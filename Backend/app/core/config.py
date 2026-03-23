# ============================================================
# app/core/config.py
# Cấu hình tập trung toàn bộ dự án (đọc từ .env)
# ============================================================
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────
    APP_NAME: str = "AI Recruitment API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/ai_recruitment"

    # ── JWT ──────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_SUPER_SECRET_KEY_32CHARS"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 giờ

    # ── Super Admin Seed ─────────────────────────────────────
    SUPER_ADMIN_EMAIL: str = "admin@company.com"
    SUPER_ADMIN_PASSWORD: str = "Admin@12345"

    # ── File Upload Limits ───────────────────────────────────
    MAX_FILE_SIZE_MB: int = 5
    MAX_PDF_PAGES: int = 5

    # ── Storage ──────────────────────────────────────────────
    CV_UPLOAD_DIR: str = "storage/cvs"
    LOG_DIR: str = "logs"
    AI_MODEL_DIR: str = "app/ai_models"  # Thư mục chứa rf_model.joblib

    model_config = ConfigDict(env_file=".env", case_sensitive=True)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
