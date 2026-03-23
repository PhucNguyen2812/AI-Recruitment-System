# ============================================================
# app/services/auth_service.py
# Business logic: Login, Create HR, Seed Super Admin
# ============================================================
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import NguoiDung, VaiTro
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import get_settings
from app.core.logger import action_logger, error_logger

settings = get_settings()


def seed_super_admin(db: Session) -> None:
    """
    Khởi tạo tài khoản Super Admin nếu chưa tồn tại.
    Gọi khi startup FastAPI.
    """
    existing = db.query(NguoiDung).filter(
        NguoiDung.vai_tro == VaiTro.quan_tri_vien
    ).first()
    if existing:
        return  # Đã có rồi, không cần seed

    admin = NguoiDung(
        id=uuid.uuid4(),
        email=settings.SUPER_ADMIN_EMAIL,
        mat_khau_ma_hoa=hash_password(settings.SUPER_ADMIN_PASSWORD),
        vai_tro=VaiTro.quan_tri_vien,
    )
    db.add(admin)
    db.commit()
    action_logger.info("Super Admin seeded: email=%s", settings.SUPER_ADMIN_EMAIL)


def login(db: Session, email: str, mat_khau: str, ip: str = "unknown") -> dict:
    """
    Xác thực email/password, trả về access token.
    """
    user = db.query(NguoiDung).filter(NguoiDung.email == email).first()
    if not user or not verify_password(mat_khau, user.mat_khau_ma_hoa):
        error_logger.warning("Login failed for email=%s from IP=%s", email, ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không đúng.",
        )

    # Single Session: Tạo session_id mới mỗi lần login
    session_id = str(uuid.uuid4())
    user.phien_dang_nhap = session_id
    db.commit()

    token = create_access_token(data={
        "sub": str(user.id),
        "role": user.vai_tro.value,
        "sid": session_id
    })
    action_logger.info("LOGIN | user_id=%s | vai_tro=%s | session_id=%s | IP=%s", user.id, user.vai_tro.value, session_id, ip)
    return {
        "access_token": token,
        "token_type": "bearer",
        "vai_tro": user.vai_tro,
    }


def create_hr_account(db: Session, email: str, mat_khau: str, created_by: NguoiDung) -> NguoiDung:
    """
    Super Admin tạo tài khoản HR mới.
    """
    existing = db.query(NguoiDung).filter(NguoiDung.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{email}' đã được sử dụng.",
        )

    hr = NguoiDung(
        id=uuid.uuid4(),
        email=email,
        mat_khau_ma_hoa=hash_password(mat_khau),
        vai_tro=VaiTro.nhan_su,
    )
    db.add(hr)
    db.commit()
    db.refresh(hr)

    action_logger.info(
        "CREATE_HR | new_hr_id=%s | email=%s | created_by=%s",
        hr.id, hr.email, created_by.id,
    )
    return hr
