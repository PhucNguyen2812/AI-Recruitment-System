# ============================================================
# app/models/user.py
# ORM Model: nguoi_dung (User / HR)
# ============================================================
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Enum as SAEnum, DateTime
from app.core.database import Base
from app.core.types import GUID
import enum


class VaiTro(str, enum.Enum):
    quan_tri_vien = "quan_tri_vien"   # Super Admin
    nhan_su = "nhan_su"               # HR


class NguoiDung(Base):
    __tablename__ = "nguoi_dung"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    mat_khau_ma_hoa = Column(String(255), nullable=False)
    vai_tro = Column(SAEnum(VaiTro), nullable=False, default=VaiTro.nhan_su)
    phien_dang_nhap = Column(String(255), nullable=True)  # ID phiên hiện tại
    ngay_tao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
