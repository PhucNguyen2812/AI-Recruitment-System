# ============================================================
# app/models/notification.py
# ORM Model: nhat_ky_thong_bao (System Notifications)
# ============================================================
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from app.core.database import Base
from app.core.types import GUID


class NhatKyThongBao(Base):
    __tablename__ = "nhat_ky_thong_bao"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_nguoi_dung = Column(
        GUID(),
        ForeignKey("nguoi_dung.id", ondelete="CASCADE"),
        nullable=False,
    )
    noi_dung = Column(String(2000), nullable=False)
    da_doc = Column(Boolean, default=False)
    loai = Column(String(50))  # e.g. 'pass_ai', 'fail_ai', 'system'
    ngay_tao = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
