# ============================================================
# app/schemas/campaign.py
# Pydantic Schemas for Campaign Operations
# ============================================================
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from app.models.campaign import TrangThaiChienDich
from app.schemas.job import JobResponse


class CampaignBase(BaseModel):
    tieu_de: str
    mo_ta: Optional[str] = None
    ngay_bat_dau: datetime
    ngay_ket_thuc: datetime
    trang_thai: TrangThaiChienDich = TrangThaiChienDich.dang_mo


class CampaignCreate(CampaignBase):
    @field_validator("ngay_bat_dau")
    @classmethod
    def validate_ngay_bat_dau(cls, v: datetime) -> datetime:
        now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        v_utc = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        if v_utc < now:
            raise ValueError("Ngày bắt đầu không được nhỏ hơn ngày hôm nay.")
        return v

    @model_validator(mode="after")
    def validate_dates(self):
        if self.ngay_ket_thuc <= self.ngay_bat_dau:
            raise ValueError("Ngày kết thúc phải sau ngày bắt đầu.")
        return self


class CampaignUpdate(BaseModel):
    """Chỉ cho phép sửa: tieu_de, mo_ta, ngay_ket_thuc.
    Không cho phép sửa: ngay_bat_dau, trang_thai (dùng endpoint riêng)."""
    tieu_de: Optional[str] = None
    mo_ta: Optional[str] = None
    ngay_ket_thuc: Optional[datetime] = None

    @field_validator("ngay_ket_thuc")
    @classmethod
    def validate_ngay_ket_thuc(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            now = datetime.now(timezone.utc)
            v_utc = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
            if v_utc < now:
                raise ValueError("Ngày kết thúc mới không được nhỏ hơn thời điểm hiện tại.")
        return v


class CampaignResponse(CampaignBase):
    id: UUID
    creator_id: UUID
    ngay_tao: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CampaignDetailResponse(CampaignResponse):
    cong_viec: List[JobResponse] = []
