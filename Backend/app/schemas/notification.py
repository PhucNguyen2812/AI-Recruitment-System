from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class NotificationBase(BaseModel):
    noi_dung: str
    da_doc: bool
    loai: Optional[str] = None
    ngay_tao: datetime

class NotificationRead(NotificationBase):
    id: int
    id_nguoi_dung: UUID

    class Config:
        from_attributes = True
