# ============================================================
# app/models/audit_log.py
# ORM Model: nhat_ky_he_thong (Audit Logs)
# ============================================================
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from app.core.database import Base
from app.core.types import GUID


class NhatKyHeThong(Base):
    __tablename__ = "nhat_ky_he_thong"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_nguoi_dung = Column(
        GUID(),
        ForeignKey("nguoi_dung.id", ondelete="SET NULL"),
        nullable=True,
    )
    hanh_dong = Column(String(100), nullable=False)
    chi_tiet = Column(String(2000), nullable=True)  # JSON string (SQLite compat)
    dia_chi_ip = Column(String(45), nullable=True)
    ngay_tao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
