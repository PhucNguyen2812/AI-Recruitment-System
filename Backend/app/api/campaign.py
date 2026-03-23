# ============================================================
# app/api/campaign.py
# API router for Campaign Operations
# ============================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignDetailResponse
from app.schemas.ranking_archive import RankingArchiveResponse
from app.services import campaign_service
from app.middleware.auth_middleware import get_current_user
from app.models.user import NguoiDung

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])


@router.get("/", response_model=List[CampaignResponse])
def get_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return campaign_service.get_campaigns(db, skip=skip, limit=limit)


@router.get("/my", response_model=List[CampaignResponse])
def get_my_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    return campaign_service.get_campaigns(db, skip=skip, limit=limit, creator_id=current_user.id)


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    return campaign_service.create_campaign(db=db, campaign=campaign, creator_id=current_user.id)


@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
def get_campaign(campaign_id: str, db: Session = Depends(get_db)):
    db_campaign = campaign_service.get_campaign_by_id(db, campaign_id=campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return db_campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(campaign_id: str, campaign_update: CampaignUpdate, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    db_campaign = campaign_service.get_campaign_by_id(db, campaign_id=campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if db_campaign.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this campaign")
    # Chỉ cho phép sửa khi campaign đang mở
    from app.models.campaign import TrangThaiChienDich
    if db_campaign.trang_thai == TrangThaiChienDich.da_dong:
        raise HTTPException(status_code=400, detail="Không thể chỉnh sửa đợt tuyển dụng đã đóng.")
    return campaign_service.update_campaign(db=db, db_campaign=db_campaign, campaign_update=campaign_update)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(campaign_id: str, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    db_campaign = campaign_service.get_campaign_by_id(db, campaign_id=campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if db_campaign.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this campaign")
    campaign_service.delete_campaign(db=db, db_campaign=db_campaign)
    return {"message": "Campaign deleted"}


# ─────────────────────────────────────────────────────────────
# Đóng đợt tuyển dụng sớm
# ─────────────────────────────────────────────────────────────
@router.post("/{campaign_id}/close-early", status_code=status.HTTP_200_OK)
def close_campaign_early(campaign_id: str, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    """
    Đóng đợt tuyển dụng sớm:
    - Snapshot AHP ranking top 30 (10 top + 20 dự bị) cho mỗi Job
    - Xóa dữ liệu cá nhân ứng viên (privacy compliance)
    - Chuyển trạng thái campaign + tất cả jobs sang 'da_dong'
    """
    db_campaign = campaign_service.get_campaign_by_id(db, campaign_id=campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Không tìm thấy đợt tuyển dụng")
    if db_campaign.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Không có quyền đóng đợt tuyển dụng này")
    
    try:
        result = campaign_service.close_campaign_early(
            db=db,
            campaign_id=campaign_id,
            hr_user_id=str(current_user.id),
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─────────────────────────────────────────────────────────────
# Lấy kết quả xếp hạng đã lưu trữ (archive)
# ─────────────────────────────────────────────────────────────
@router.get("/{campaign_id}/archive", response_model=List[RankingArchiveResponse])
def get_campaign_archive(
    campaign_id: str, 
    job_id: Optional[str] = None, 
    db: Session = Depends(get_db), 
    current_user: NguoiDung = Depends(get_current_user)
):
    """Lấy dữ liệu xếp hạng đã archive cho campaign đã đóng."""
    db_campaign = campaign_service.get_campaign_by_id(db, campaign_id=campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Không tìm thấy đợt tuyển dụng")
    
    return campaign_service.get_ranking_archive(db, campaign_id=campaign_id, job_id=job_id)
