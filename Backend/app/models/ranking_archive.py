# ============================================================
# app/models/ranking_archive.py
# ORM Model: ket_qua_xep_hang (Lưu trữ kết quả xếp hạng AHP)
# Snapshot kết quả khi đóng đợt tuyển dụng
# ============================================================
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey
from app.core.database import Base
from app.core.types import GUID


class KetQuaXepHang(Base):
    __tablename__ = "ket_qua_xep_hang"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)

    # ── Liên kết ──
    id_chien_dich = Column(GUID(), ForeignKey("chien_dich.id"), nullable=False, index=True)
    id_cong_viec = Column(GUID(), nullable=False, index=True)  # Không FK vì job vẫn tồn tại nhưng có thể bị xóa sau

    # ── Thông tin ứng viên (snapshot — dữ liệu gốc sẽ bị xóa) ──
    ho_ten = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    so_dien_thoai = Column(String(20), nullable=True)

    # ── Kết quả AHP ──
    hang = Column(Integer, nullable=False)       # 1-30
    diem_ahp = Column(Float, nullable=False)
    nhom = Column(String(20), nullable=False)     # "top10" | "du_bi"

    # ── Chi tiết điểm từng tiêu chí (JSON) ──
    diem_chi_tiet = Column(JSON, nullable=True)
    # VD: {"ky_thuat": 7.5, "hoc_van": 8.0, "ngoai_ngu": 6.0, "tich_cuc": 9.0}

    # ── Metadata (snapshot tên để hiển thị khi data gốc bị xóa) ──
    ten_cong_viec = Column(String(255), nullable=True)
    ten_chien_dich = Column(String(255), nullable=True)

    # ── Timestamps ──
    ngay_luu = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
