# ============================================================
# app/models/position.py
# ORM Model: vi_tri (Danh sách Vị trí chuyên môn)
# ============================================================
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from app.core.database import Base
from app.core.types import GUID


class ViTri(Base):
    __tablename__ = "vi_tri"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    ten = Column(String(255), nullable=False)
    ma = Column(String(50), nullable=False, unique=True, index=True) # VD: IT_Intern
    mo_ta = Column(Text, nullable=True)
    ngay_tao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
