# ============================================================
# app/services/dashboard_service.py
# Service for Dashboard Statistics
# ============================================================
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.campaign import ChienDich, TrangThaiChienDich
from app.models.job import CongViec
from app.models.application import DonUngTuyen, TrangThaiDon


def get_dashboard_stats(db: Session):
    """
    Calculate real-time dashboard statistics.
    Returns:
        dict: Stats including active campaigns, total jobs, applications, and rejected by AI.
    """
    # Active Campaigns
    active_campaigns_count = db.query(func.count(ChienDich.id)).filter(
        ChienDich.trang_thai == TrangThaiChienDich.dang_mo
    ).scalar()

    # Total Jobs
    total_jobs_count = db.query(func.count(CongViec.id)).scalar()

    # Total Applications
    total_applications_count = db.query(func.count(DonUngTuyen.id)).scalar()

    # Rejected Apps (Specifically by RF/AI model)
    rejected_apps_count = db.query(func.count(DonUngTuyen.id)).filter(
        DonUngTuyen.trang_thai == TrangThaiDon.khong_phu_hop
    ).scalar()

    return {
        "active_campaigns": active_campaigns_count,
        "total_jobs": total_jobs_count,
        "total_applications": total_applications_count,
        "rejected_applications": rejected_apps_count
    }
