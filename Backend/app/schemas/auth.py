# ============================================================
# app/schemas/auth.py
# Pydantic schemas cho Authentication
# ============================================================
from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.models.user import VaiTro


class LoginRequest(BaseModel):
    email: EmailStr
    mat_khau: str

    model_config = {"json_schema_extra": {"example": {"email": "hr@company.com", "mat_khau": "Password123"}}}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    vai_tro: VaiTro


class CreateHRRequest(BaseModel):
    email: EmailStr
    mat_khau: str

    model_config = {"json_schema_extra": {"example": {"email": "hr_new@company.com", "mat_khau": "SecurePass!1"}}}


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    vai_tro: VaiTro

    model_config = {"from_attributes": True}
