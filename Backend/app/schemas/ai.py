# ============================================================
# app/schemas/ai.py
# Pydantic Schemas cho AI Pipeline endpoints (RF + AHP)
# ============================================================
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from uuid import UUID


# ─────────────────────────────────────────────────────────────
# RF Schemas
# ─────────────────────────────────────────────────────────────

class RFBatchRequest(BaseModel):
    job_id: UUID = Field(..., description="UUID của tin tuyển dụng")
    position: Optional[str] = Field(
        None,
        description="Vị trí cố định: IT_Intern hoặc Marketing_Intern",
        examples=["IT_Intern", "Marketing_Intern"],
    )

    @field_validator("position")
    @classmethod
    def validate_position(cls, v):
        VALID_POSITIONS = ["IT_Intern", "Marketing_Intern", None]
        if v is not None and v not in VALID_POSITIONS:
            raise ValueError(
                f"Vị trí không hợp lệ. Chỉ chấp nhận: {', '.join(p for p in VALID_POSITIONS if p)}"
            )
        return v


class RFBatchResponse(BaseModel):
    job_id: UUID
    total: int = Field(..., description="Tổng số đơn đã xử lý")
    passed: int = Field(..., description="Số CV qua vòng RF")
    rejected: int = Field(..., description="Số CV bị loại (đã Hard Delete)")
    errors: int = Field(..., description="Số lỗi xử lý")
    all_rejected: bool = Field(..., description="True nếu 100% CV bị loại")
    message: str


class RFSingleRequest(BaseModel):
    """Dùng để test predict 1 đơn cụ thể (debug endpoint)."""
    don_id: UUID
    position: Optional[str] = None


class RFSingleResponse(BaseModel):
    don_id: UUID
    prediction: int = Field(..., description="1=hợp lệ, 0=rác")
    probability: float = Field(..., description="Xác suất hợp lệ (0-1)")
    language: str = Field(..., description="Ngôn ngữ phát hiện: en/vi")
    keyword_count: int
    text_length: int
    action: str = Field(..., description="passed | rejected | error")


# ─────────────────────────────────────────────────────────────
# AHP Schemas
# ─────────────────────────────────────────────────────────────

class AHPValidateRequest(BaseModel):
    matrix: list[list[float]] = Field(
        ...,
        description="Ma trận so sánh cặp 4×4 (Pairwise Comparison Matrix)",
        examples=[
            [
                [1, 3, 5, 7],
                [1/3, 1, 3, 5],
                [1/5, 1/3, 1, 3],
                [1/7, 1/5, 1/3, 1],
            ]
        ],
    )

    @field_validator("matrix")
    @classmethod
    def validate_matrix_shape(cls, v):
        if len(v) != 4:
            raise ValueError("Ma trận phải có đúng 4 hàng (4 tiêu chí)")
        for row in v:
            if len(row) != 4:
                raise ValueError("Mỗi hàng phải có đúng 4 phần tử")
        return v


class AHPValidateResponse(BaseModel):
    is_consistent: bool
    cr: float = Field(..., description="Consistency Ratio")
    ci: float = Field(..., description="Consistency Index")
    lambda_max: float
    weights: dict[str, float] = Field(
        ...,
        description="Trọng số 4 tiêu chí: ky_thuat, hoc_van, ngoai_ngu, tich_cuc",
    )
    message: str


class AHPRequest(BaseModel):
    job_id: UUID = Field(..., description="UUID của tin tuyển dụng")
    matrix: list[list[float]] = Field(
        ...,
        description="Ma trận so sánh cặp 4×4",
    )

    @field_validator("matrix")
    @classmethod
    def validate_matrix_shape(cls, v):
        if len(v) != 4:
            raise ValueError("Ma trận phải có đúng 4 hàng")
        for row in v:
            if len(row) != 4:
                raise ValueError("Mỗi hàng phải có đúng 4 phần tử")
        return v


class CandidateRankItem(BaseModel):
    """Thông tin 1 ứng viên trong bảng xếp hạng AHP."""
    don_id: str
    candidate_name: str
    candidate_id: str
    rank: int
    ahp_score: float
    scores: dict[str, float] = Field(
        ...,
        description="Điểm thô theo từng tiêu chí: ky_thuat, hoc_van, ngoai_ngu, tich_cuc",
    )


class ConsistencyInfo(BaseModel):
    lambda_max: float
    ci: float
    ri: float
    cr: float


class AHPResponse(BaseModel):
    job_id: UUID
    top_10: list[CandidateRankItem] = Field(..., description="Top 10 ứng viên")
    reserve_20: list[CandidateRankItem] = Field(..., description="20 ứng viên dự bị")
    total_ranked: int
    weights: dict[str, float]
    consistency: Optional[ConsistencyInfo] = None
    message: str


class AHPConfigSaveRequest(BaseModel):
    job_id: UUID = Field(..., description="UUID của tin tuyển dụng")
    matrix: list[list[float]] = Field(
        ...,
        description="Ma trận so sánh cặp 4×4",
    )

    @field_validator("matrix")
    @classmethod
    def validate_matrix_shape(cls, v):
        if len(v) != 4:
            raise ValueError("Ma trận phải có đúng 4 hàng")
        for row in v:
            if len(row) != 4:
                raise ValueError("Mỗi hàng phải có đúng 4 phần tử")
        return v


class AHPConfigSaveResponse(BaseModel):
    job_id: UUID
    is_consistent: bool
    weights: dict[str, float]
    consistency: ConsistencyInfo
    message: str


class AHPRankRequest(BaseModel):
    job_id: UUID = Field(..., description="UUID của tin tuyển dụng")
