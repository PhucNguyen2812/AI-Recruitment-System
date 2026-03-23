# ============================================================
# app/api/dashboard.py
# API router for Dashboard Statistics
# ============================================================
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.dashboard import DashboardStatsResponse
from app.services import dashboard_service
from app.middleware.auth_middleware import get_current_user
from app.models.user import NguoiDung

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
):
    """
    Get real-time statistics for the dashboard.
    Protected by JWT.
    """
    return dashboard_service.get_dashboard_stats(db)
