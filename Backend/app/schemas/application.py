# ============================================================
# app/schemas/application.py
# Pydantic schemas cho CV Upload & ứng tuyển
# ============================================================
from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from datetime import datetime
from app.models.application import TrangThaiDon


class CandidateRegisterRequest(BaseModel):
    email: EmailStr
    ho_ten: str
    so_dien_thoai: Optional[str] = None


class UploadCVResponse(BaseModel):
    don_id: UUID
    message: str
    trang_thai: TrangThaiDon


class ApplicationDetail(BaseModel):
    id: UUID
    id_ung_vien: UUID
    id_cong_viec: UUID
    ma_hash_cv: str
    diem_rf: Optional[int]
    diem_ahp: Optional[float]
    trang_thai: TrangThaiDon
    ngay_nop: datetime

    model_config = {"from_attributes": True}
