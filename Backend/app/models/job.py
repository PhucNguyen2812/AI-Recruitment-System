# ============================================================
# app/models/job.py
# ORM Model: cong_viec (Tin tuyển dụng)
# ============================================================
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Enum as SAEnum, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.types import GUID
import enum

class TrangThaiCongViec(str, enum.Enum):
    dang_mo = "dang_mo"
    da_dong = "da_dong"

class CongViec(Base):
    __tablename__ = "cong_viec"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tieu_de = Column(String(255), nullable=False)
    
    # FK References
    id_vi_tri = Column(GUID(), ForeignKey("vi_tri.id"), nullable=False, index=True)
    campaign_id = Column(GUID(), ForeignKey("chien_dich.id", ondelete="CASCADE"), nullable=False, index=True)
    creator_id = Column(GUID(), ForeignKey("nguoi_dung.id"), nullable=False)
    
    mo_ta = Column(Text, nullable=True)
    yeu_cau = Column(Text, nullable=True)
    trang_thai = Column(
        SAEnum(TrangThaiCongViec),
        nullable=False,
        default=TrangThaiCongViec.dang_mo,
    )
    ahp_weights = Column(JSON, nullable=True)  # Lưu cấu hình trọng số AHP cuối cùng
    ngay_tao = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    chien_dich = relationship("ChienDich", back_populates="cong_viec")
    vi_tri = relationship("ViTri")
    creator = relationship("NguoiDung")
