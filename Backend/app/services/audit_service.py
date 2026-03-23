# ============================================================
# app/services/audit_service.py
# Business logic: Ghi nhật ký hệ thống (Audit Logs)
# ============================================================
from sqlalchemy.orm import Session
from app.models.audit_log import NhatKyHeThong


def log_action(
    db: Session,
    user_id: str,
    action: str,
    details: str,
    ip_address: str = None,
) -> NhatKyHeThong:
    """
    Ghi lại một hành động vào nhật ký hệ thống.
    """
    audit = NhatKyHeThong(
        id_nguoi_dung=user_id,
        hanh_dong=action,
        chi_tiet=details,
        dia_chi_ip=ip_address,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit
