# ============================================================
# app/main.py
# FastAPI Application Entry Point
# ============================================================
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logger import action_logger, error_logger
from app.api import auth, cv, ai, notification, admin, campaign, position, job, dashboard
from app.services.auth_service import seed_super_admin

settings = get_settings()


# ── Lifespan (startup / shutdown) ─────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    action_logger.info("=== AI Recruitment API starting up ===")

    # Import at runtime để test có thể patch trước khi gọi
    import app.core.database as db_module
    import app.models.ranking_archive  # Đảm bảo model mới được đăng ký
    db_module.Base.metadata.create_all(bind=db_module.engine)

    # Seed Super Admin
    db = db_module.SessionLocal()
    try:
        seed_super_admin(db)
    finally:
        db.close()

    # Tạo thư mục lưu CV, logs và AI models
    os.makedirs(settings.CV_UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    os.makedirs("app/ai_models", exist_ok=True)

    # Preload RF model nếu đã được train
    model_path = os.path.join("app", "ai_models", "rf_model.joblib")
    if os.path.exists(model_path):
        try:
            from app.services.rf_service import _load_model
            _load_model()
            action_logger.info("RF model preloaded successfully.")
        except Exception as e:
            action_logger.warning("RF model preload failed: %s", str(e))
    else:
        action_logger.warning(
            "RF model not found at '%s'. Run: python train_rf_model.py", model_path
        )

    yield

    # SHUTDOWN
    action_logger.info("=== AI Recruitment API shutting down ===")



# ── App Instance ──────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Backend API cho Hệ thống Tuyển dụng AI. "
        "Sử dụng Random Forest (lọc CV rác) + AHP (xếp hạng ứng viên)."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handler ──────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_logger.exception("Unhandled exception on %s %s: %s", request.method, request.url, str(exc))
    return JSONResponse(
        status_code=500,
        content={"detail": "Lỗi hệ thống nội bộ. Vui lòng thử lại sau."},
    )


# ── Routers ───────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(cv.router)
app.include_router(ai.router)
app.include_router(notification.router)
app.include_router(admin.router)
app.include_router(campaign.router)
app.include_router(position.router)
app.include_router(job.router)
app.include_router(dashboard.router)


# ── Health Check ──────────────────────────────────────────
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
