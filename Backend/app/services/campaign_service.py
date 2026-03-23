# ============================================================
# app/services/campaign_service.py
# Service layer for Campaign business logic 
# ============================================================
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.campaign import ChienDich, TrangThaiChienDich
from app.models.job import CongViec, TrangThaiCongViec
from app.models.ranking_archive import KetQuaXepHang
from app.schemas.campaign import CampaignCreate, CampaignUpdate
from app.core.types import GUID
from app.core.logger import action_logger, error_logger


def get_campaigns(db: Session, skip: int = 0, limit: int = 100, creator_id: Optional[GUID] = None) -> List[ChienDich]:
    query = db.query(ChienDich)
    if creator_id:
        query = query.filter(ChienDich.creator_id == creator_id)
    return query.order_by(ChienDich.ngay_tao.desc()).offset(skip).limit(limit).all()


def get_campaign_by_id(db: Session, campaign_id: GUID) -> Optional[ChienDich]:
    return db.query(ChienDich).filter(ChienDich.id == campaign_id).first()


def create_campaign(db: Session, campaign: CampaignCreate, creator_id: GUID) -> ChienDich:
    db_campaign = ChienDich(
        **campaign.model_dump(),
        creator_id=creator_id
    )
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


def update_campaign(db: Session, db_campaign: ChienDich, campaign_update: CampaignUpdate) -> ChienDich:
    update_data = campaign_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_campaign, key, value)
    
    db.commit()
    db.refresh(db_campaign)
    return db_campaign


def delete_campaign(db: Session, db_campaign: ChienDich) -> None:
    db.delete(db_campaign)
    db.commit()


def close_campaign_early(db: Session, campaign_id: str, hr_user_id: str) -> dict:
    """
    Đóng đợt tuyển dụng sớm:
    1. Với mỗi Job đang mở: chạy AHP và snapshot top 30 vào ket_qua_xep_hang
    2. Đóng tất cả Jobs (xóa CV + DonUngTuyen + UngVien — privacy compliance)
    3. Chuyển Campaign sang trạng thái da_dong
    
    Returns:
        dict với thông tin tổng kết quá trình đóng
    """
    from app.models.application import DonUngTuyen, TrangThaiDon
    from app.models.candidate import UngVien
    from app.services.ahp_service import run_ahp_rank_only, _compute_candidate_raw_scores
    from app.services.job_service import close_job
    
    campaign = db.query(ChienDich).filter(ChienDich.id == campaign_id).first()
    if not campaign:
        raise ValueError("Không tìm thấy đợt tuyển dụng.")
    
    if campaign.trang_thai == TrangThaiChienDich.da_dong:
        raise ValueError("Đợt tuyển dụng này đã được đóng trước đó.")
    
    # Lấy tất cả Jobs trong campaign
    jobs = db.query(CongViec).filter(CongViec.campaign_id == campaign_id).all()
    
    total_archived = 0
    jobs_processed = 0
    jobs_skipped = 0
    
    for job in jobs:
        if job.trang_thai == TrangThaiCongViec.da_dong:
            jobs_skipped += 1
            continue
        
        jobs_processed += 1
        
        # ── Bước 1: Snapshot kết quả AHP (nếu có ứng viên & AHP weights) ──
        try:
            if job.ahp_weights:
                result = run_ahp_rank_only(db, str(job.id), hr_user_id)
                all_ranked = result["top_10"] + result["reserve_20"]
                
                for candidate in all_ranked:
                    # Lấy thông tin ứng viên từ DB trước khi bị xóa
                    from app.models.candidate import UngVien as UngVienModel
                    don = db.query(DonUngTuyen).filter(
                        DonUngTuyen.id == candidate["don_id"]
                    ).first()
                    
                    uv = None
                    if don:
                        uv = db.query(UngVienModel).filter(
                            UngVienModel.id == don.id_ung_vien
                        ).first()
                    
                    is_top10 = candidate["rank"] <= 10
                    
                    archive_record = KetQuaXepHang(
                        id_chien_dich=campaign.id,
                        id_cong_viec=job.id,
                        ho_ten=candidate["candidate_name"],
                        email=uv.email if uv else "N/A",
                        so_dien_thoai=uv.so_dien_thoai if uv else None,
                        hang=candidate["rank"],
                        diem_ahp=candidate["ahp_score"],
                        nhom="top10" if is_top10 else "du_bi",
                        diem_chi_tiet=candidate.get("scores", {}),
                        ten_cong_viec=job.tieu_de,
                        ten_chien_dich=campaign.tieu_de,
                    )
                    db.add(archive_record)
                    total_archived += 1
                
                db.flush()
                
                action_logger.info(
                    "CAMPAIGN_CLOSE_SNAPSHOT | campaign=%s | job=%s | archived=%d",
                    campaign_id, str(job.id), len(all_ranked),
                )
        except ValueError as e:
            # Nếu không có ứng viên hoặc chưa cấu hình AHP → bỏ qua, không crash
            action_logger.warning(
                "CAMPAIGN_CLOSE_SKIP_AHP | campaign=%s | job=%s | reason=%s",
                campaign_id, str(job.id), str(e),
            )
        except Exception as e:
            error_logger.error(
                "CAMPAIGN_CLOSE_ERROR | campaign=%s | job=%s | error=%s",
                campaign_id, str(job.id), str(e),
            )
        
        # ── Bước 2: Đóng Job (xóa CV + data — privacy compliance) ──
        close_job(db, str(job.id))
    
    # ── Bước 3: Đóng Campaign ──
    campaign.trang_thai = TrangThaiChienDich.da_dong
    db.commit()
    
    # Ghi audit log
    from app.services import audit_service
    audit_service.log_action(
        db,
        user_id=hr_user_id,
        action="CLOSE_CAMPAIGN_EARLY",
        details=f"Đợt '{campaign.tieu_de}' đã đóng sớm. {jobs_processed} job xử lý, {total_archived} kết quả đã lưu trữ.",
    )
    
    action_logger.info(
        "CAMPAIGN_CLOSED_EARLY | id=%s | jobs_processed=%d | jobs_skipped=%d | archived=%d",
        campaign_id, jobs_processed, jobs_skipped, total_archived,
    )
    
    return {
        "campaign_id": campaign_id,
        "jobs_processed": jobs_processed,
        "jobs_skipped": jobs_skipped,
        "total_archived": total_archived,
        "message": f"Đã đóng đợt tuyển dụng. {total_archived} kết quả xếp hạng đã được lưu trữ.",
    }


def get_ranking_archive(db: Session, campaign_id: str, job_id: Optional[str] = None) -> List[KetQuaXepHang]:
    """Lấy kết quả xếp hạng đã lưu trữ cho 1 campaign (hoặc 1 job cụ thể)."""
    query = db.query(KetQuaXepHang).filter(KetQuaXepHang.id_chien_dich == campaign_id)
    if job_id:
        query = query.filter(KetQuaXepHang.id_cong_viec == job_id)
    return query.order_by(KetQuaXepHang.hang.asc()).all()
