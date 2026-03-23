# ============================================================
# app/middleware/auth_middleware.py
# FastAPI dependency: xác thực JWT và lấy current user
# ============================================================
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import decode_access_token
from app.core.database import get_db
from app.models.user import NguoiDung, VaiTro

bearer_scheme = HTTPBearer()


def _get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> NguoiDung:
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc đã hết hạn.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    sid = payload.get("sid")
    user = db.query(NguoiDung).filter(NguoiDung.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Người dùng không tồn tại.")

    # Single Session Check: So khớp session_id từ token với bản ghi mới nhất trong DB
    if sid != user.phien_dang_nhap:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Phiên làm việc đã hết hạn hoặc đã đăng nhập từ nơi khác.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_admin(current_user: NguoiDung = Depends(_get_current_user)) -> NguoiDung:
    """Chỉ Super Admin mới được phép."""
    if current_user.vai_tro != VaiTro.quan_tri_vien:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Super Admin mới có quyền thực hiện hành động này.",
        )
    return current_user


def require_hr_or_admin(current_user: NguoiDung = Depends(_get_current_user)) -> NguoiDung:
    """HR và Admin đều được phép."""
    if current_user.vai_tro not in (VaiTro.quan_tri_vien, VaiTro.nhan_su):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Không có quyền truy cập.")
    return current_user


# Public alias
get_current_user = _get_current_user
