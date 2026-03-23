# ============================================================
# app/models/application.py
# ORM Model: don_ung_tuyen (Đơn ứng tuyển)
# ============================================================
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, Integer, Enum as SAEnum,
    DateTime, ForeignKey, Index,
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.types import GUID
import enum


class TrangThaiDon(str, enum.Enum):
    dang_cho = "dang_cho"             # Chờ AI xử lý
    da_nhan = "da_nhan"               # Passed RF, đang xếp hạng AHP
    khong_phu_hop = "khong_phu_hop"  # Bị RF reject (đã Hard Delete file)


class DonUngTuyen(Base):
    __tablename__ = "don_ung_tuyen"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    id_ung_vien = Column(GUID(), ForeignKey("ung_vien.id", ondelete="CASCADE"), nullable=False)
    id_cong_viec = Column(GUID(), ForeignKey("cong_viec.id", ondelete="CASCADE"), nullable=False, index=True)
    duong_dan_cv = Column(String(500), nullable=True)    # None sau Hard Delete
    ma_hash_cv = Column(String(32), nullable=False, index=True)  # MD5, dùng chặn spam
    diem_rf = Column(Integer, nullable=True)             # 0=Rác, 1=Đạt
    diem_ahp = Column(Float, nullable=True)              # Score xếp hạng cuối
    trang_thai = Column(
        SAEnum(TrangThaiDon),
        nullable=False,
        default=TrangThaiDon.dang_cho,
    )
    ngay_nop = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    ung_vien = relationship("UngVien", backref="don_ung_tuyen")
    cong_viec = relationship("CongViec", backref="don_ung_tuyen")

    # Composite index cho việc truy vấn nhanh theo job
    __table_args__ = (
        Index("ix_don_ung_tuyen_job_status", "id_cong_viec", "trang_thai"),
    )
