# ============================================================
# app/schemas/job.py
# Pydantic Schemas for Job Operations
# ============================================================
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from app.models.job import TrangThaiCongViec


class JobBase(BaseModel):
    tieu_de: str
    mo_ta: Optional[str] = None
    yeu_cau: Optional[str] = None
    id_vi_tri: UUID
    campaign_id: UUID
    trang_thai: TrangThaiCongViec = TrangThaiCongViec.dang_mo
    ahp_weights: Optional[Dict[str, Any]] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    tieu_de: Optional[str] = None
    mo_ta: Optional[str] = None
    yeu_cau: Optional[str] = None
    trang_thai: Optional[TrangThaiCongViec] = None
    ahp_weights: Optional[Dict[str, Any]] = None


class JobResponse(JobBase):
    id: UUID
    creator_id: UUID
    ngay_tao: datetime
    
    model_config = ConfigDict(from_attributes=True)
