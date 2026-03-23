# ============================================================
# app/schemas/ranking_archive.py
# Pydantic Schemas for Ranking Archive (kết quả xếp hạng đã lưu)
# ============================================================
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class RankingArchiveResponse(BaseModel):
    id: UUID
    id_chien_dich: UUID
    id_cong_viec: UUID
    ho_ten: str
    email: str
    so_dien_thoai: Optional[str] = None
    hang: int
    diem_ahp: float
    nhom: str
    diem_chi_tiet: Optional[Dict[str, Any]] = None
    ten_cong_viec: Optional[str] = None
    ten_chien_dich: Optional[str] = None
    ngay_luu: datetime

    model_config = ConfigDict(from_attributes=True)
