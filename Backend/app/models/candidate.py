# ============================================================
# app/models/candidate.py
# ORM Model: ung_vien (Ứng viên)
# ============================================================
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from app.core.database import Base
from app.core.types import GUID


class UngVien(Base):
    __tablename__ = "ung_vien"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, index=True)
    ho_ten = Column(String(255), nullable=False)
    so_dien_thoai = Column(String(20), nullable=True)
    file_hash = Column(String(32), nullable=True, index=True)  # Lưu MD5 hash của CV
    id_cong_viec = Column(GUID(), ForeignKey("cong_viec.id", ondelete="CASCADE"), nullable=True)
    ngay_tao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint('email', 'id_cong_viec', name='unique_candidate_job'),
    )
