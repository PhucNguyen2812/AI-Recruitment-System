# ============================================================
# app/routers/auth.py
# Router: /api/auth
# ============================================================
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, CreateHRRequest, UserResponse
from app.services import auth_service
from app.middleware.auth_middleware import require_admin

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="Đăng nhập (HR & Admin)")
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Nhận email + mật khẩu, trả về JWT access token.
    Hoạt động cho cả Super Admin và HR.
    """
    ip = request.client.host if request.client else "unknown"
    return auth_service.login(db, body.email, body.mat_khau, ip=ip)


@router.post(
    "/create-hr",
    response_model=UserResponse,
    summary="Tạo tài khoản HR (Chỉ Super Admin)",
    status_code=201,
)
def create_hr(
    body: CreateHRRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """
    Chỉ Super Admin mới được tạo tài khoản HR.
    JWT phải được gửi trong header: Authorization: Bearer <token>
    """
    return auth_service.create_hr_account(db, body.email, body.mat_khau, created_by=current_user)


@router.get("/me", response_model=UserResponse, summary="Lấy thông tin user hiện tại")
def me(current_user=Depends(require_admin)):
    """Trả về thông tin user đang đăng nhập (dùng cho debug & whoami)."""
    return current_user
