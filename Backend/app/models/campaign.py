# ============================================================
# app/models/campaign.py
# ORM Model: chien_dich (Đợt tuyển dụng)
# ============================================================
import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.types import GUID


class TrangThaiChienDich(str, enum.Enum):
    dang_mo = "dang_mo"
    da_dong = "da_dong"


class ChienDich(Base):
    __tablename__ = "chien_dich"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tieu_de = Column(String(255), nullable=False)
    mo_ta = Column(Text, nullable=True)
    ngay_bat_dau = Column(DateTime(timezone=True), nullable=False)
    ngay_ket_thuc = Column(DateTime(timezone=True), nullable=False)
    trang_thai = Column(
        SAEnum(TrangThaiChienDich),
        nullable=False,
        default=TrangThaiChienDich.dang_mo,
    )
    creator_id = Column(GUID(), ForeignKey("nguoi_dung.id"), nullable=False)
    ngay_tao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    cong_viec = relationship("CongViec", back_populates="chien_dich", cascade="all, delete-orphan")
    creator = relationship("NguoiDung")
