# ============================================================
# app/schemas/position.py
# Pydantic Schemas for Position Operations
# ============================================================
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID


class PositionBase(BaseModel):
    ten: str
    ma: str
    mo_ta: Optional[str] = None


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    ten: Optional[str] = None
    ma: Optional[str] = None
    mo_ta: Optional[str] = None


class PositionResponse(PositionBase):
    id: UUID
    ngay_tao: datetime
    
    model_config = ConfigDict(from_attributes=True)
