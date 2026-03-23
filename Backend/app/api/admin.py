# ============================================================
# app/routers/admin.py
# API endpoints for Super Admin (Audit Logs, etc.)
# ============================================================
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import NguoiDung
from app.models.audit_log import NhatKyHeThong
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/admin", tags=["Admin"])

class AuditLogRead(BaseModel):
    id: int
    id_nguoi_dung: str | None
    hanh_dong: str
    chi_tiet: str | None
    dia_chi_ip: str | None
    ngay_tao: datetime

    class Config:
        from_attributes = True

@router.get("/audit-logs", response_model=List[AuditLogRead])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    """
    Returns all audit logs. Only for users with role 'admin'.
    """
    if current_user.vai_tro != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ Super Admin mới có quyền xem nhật ký hệ thống."
        )
    
    logs = db.query(NhatKyHeThong).order_by(NhatKyHeThong.ngay_tao.desc()).limit(100).all()
    
    # Convert GUID to string for Pydantic
    formatted_logs = []
    for log in logs:
        formatted_logs.append({
            "id": log.id,
            "id_nguoi_dung": str(log.id_nguoi_dung) if log.id_nguoi_dung else None,
            "hanh_dong": log.hanh_dong,
            "chi_tiet": log.chi_tiet,
            "dia_chi_ip": log.dia_chi_ip,
            "ngay_tao": log.ngay_tao
        })
        
    return formatted_logs
