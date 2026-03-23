# ============================================================
# app/schemas/dashboard.py
# Pydantic Schemas for Dashboard Statistics
# ============================================================
from pydantic import BaseModel

class DashboardStatsResponse(BaseModel):
    active_campaigns: int
    total_jobs: int
    total_applications: int
    rejected_applications: int

    class Config:
        from_attributes = True
