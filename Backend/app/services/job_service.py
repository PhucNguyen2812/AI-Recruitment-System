# ============================================================
# app/services/job_service.py
# Business logic: Quản lý tin tuyển dụng (Job management)
# ============================================================
import os
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.job import CongViec, TrangThaiCongViec
from app.models.application import DonUngTuyen
from app.models.candidate import UngVien
from app.core.logger import action_logger, error_logger
from app.services import audit_service
from app.schemas.job import JobCreate, JobUpdate
from app.core.types import GUID


def get_jobs(db: Session, skip: int = 0, limit: int = 100, campaign_id: Optional[GUID] = None, creator_id: Optional[GUID] = None) -> List[CongViec]:
    query = db.query(CongViec)
    if campaign_id:
        query = query.filter(CongViec.campaign_id == campaign_id)
    if creator_id:
        query = query.filter(CongViec.creator_id == creator_id)
    return query.order_by(CongViec.ngay_tao.desc()).offset(skip).limit(limit).all()


def get_open_jobs(db: Session, skip: int = 0, limit: int = 100) -> List[CongViec]:
    return db.query(CongViec).filter(
        CongViec.trang_thai == TrangThaiCongViec.dang_mo
    ).order_by(CongViec.ngay_tao.desc()).offset(skip).limit(limit).all()


def get_job_by_id(db: Session, job_id: GUID) -> Optional[CongViec]:
    return db.query(CongViec).filter(CongViec.id == job_id).first()


def create_job(db: Session, job: JobCreate, creator_id: GUID) -> CongViec:
    db_job = CongViec(
        **job.model_dump(),
        creator_id=creator_id
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


def update_job(db: Session, db_job: CongViec, job_update: JobUpdate) -> CongViec:
    update_data = job_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_job, key, value)
    
    db.commit()
    db.refresh(db_job)
    return db_job


def delete_job(db: Session, db_job: CongViec) -> None:
    db.delete(db_job)
    db.commit()


def close_job(db: Session, job_id: str) -> bool:
    """
    Logic Đóng Job (Privacy Compliance):
    1. Chuyển trạng thái Job sang 'da_dong'.
    2. Tìm tất cả Đơn ứng tuyển (DonUngTuyen) của Job này.
    3. Xóa các tệp PDF vật lý liên quan trong storage/cvs/.
    4. Xóa các bản ghi DonUngTuyen và UngVien liên quan để bảo vệ quyền riêng tư.
    """
    job = db.query(CongViec).filter(CongViec.id == job_id).first()
    if not job:
        action_logger.warning(f"CLOSE_JOB_FAILED | job_id={job_id} | Reason: Job not found.")
        return False

    # 1. Cập nhật trạng thái Job
    job.trang_thai = TrangThaiCongViec.da_dong
    db.flush()

    # 2. Tìm tất cả đơn ứng tuyển để xử lý xóa (Privacy Compliance)
    applications = db.query(DonUngTuyen).filter(DonUngTuyen.id_cong_viec == job_id).all()
    count = len(applications)

    # 3. Sử dụng hard_delete_cv để xóa từng hồ sơ + ghi Audit Log
    from app.services.cv_service import hard_delete_cv
    for app_record in applications:
        hard_delete_cv(db, app_record, reason="JOB_CLOSING")

    # 4. Đảm bảo ứng viên liên quan cũng được dọn dẹp (nếu còn sót)
    db.query(UngVien).filter(UngVien.id_cong_viec == job_id).delete(synchronize_session=False)
    db.commit()

    # Ghi Audit Log tổng quát cho việc đóng Job
    audit_service.log_action(
        db, 
        user_id=None,
        action="CLOSE_JOB",
        details=f"Job ID {job_id} đã đóng. Xóa vĩnh viễn {count} hồ sơ ứng viên.",
    )

    action_logger.info(
        f"JOB_CLOSED_SUCCESS | job_id={job_id} | Đã xóa {count} hồ sơ ứng viên liên quan."
    )
    return True
