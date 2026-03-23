# ============================================================
# app/routers/ai.py
# Router: /api/ai — RF screening + AHP ranking endpoints
# Tất cả endpoints yêu cầu HR authentication (JWT)
# ============================================================
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user, require_hr_or_admin
from app.services import rf_service, ahp_service
from app.schemas.ai import (
    RFBatchRequest,
    RFBatchResponse,
    AHPValidateRequest,
    AHPValidateResponse,
    AHPConfigSaveRequest,
    AHPConfigSaveResponse,
    AHPRankRequest,
    AHPResponse,
    RFSingleRequest,
    RFSingleResponse,
)
from app.models.user import VaiTro
from app.core.logger import action_logger

router = APIRouter(prefix="/api/ai", tags=["AI Pipeline"])




# ─────────────────────────────────────────────────────────────
# RF ENDPOINTS
# ─────────────────────────────────────────────────────────────

@router.post(
    "/rf/run-batch",
    response_model=RFBatchResponse,
    summary="Chạy RF lọc CV theo lô (Batch) cho 1 Job",
    status_code=200,
)
def run_rf_batch(
    body: RFBatchRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr_or_admin),
):
    """
    HR bấm nút "Chạy AI lọc CV".

    Hệ thống:
    1. Lấy tất cả đơn ứng tuyển `trang_thai=dang_cho` của job_id
    2. Đưa từng CV qua RF model
    3. CV rác (predict=0) → Hard Delete ngay
    4. CV hợp lệ (predict=1) → Chuyển trạng thái sang `da_nhan`
    5. Trả về thống kê

    Nếu 100% CV là rác → trả về lỗi cứng (all_rejected=True).
    """
    action_logger.info(
        "RF_BATCH_START | job_id=%s | hr=%s",
        body.job_id, current_user.id,
    )

    result = rf_service.run_rf_batch(
        db=db,
        job_id=str(body.job_id),
        position=body.position,
    )

    # Ngoại lệ: 100% CV là rác
    all_rejected = result["passed"] == 0 and result["errors"] == 0 and result["rejected"] > 0

    return RFBatchResponse(
        job_id=body.job_id,
        total=result["total"],
        passed=result["passed"],
        rejected=result["rejected"],
        errors=result["errors"],
        all_rejected=all_rejected,
        message=(
            "⚠️ Toàn bộ CV đã bị lọc là không phù hợp. Hãy xem lại hoặc thu hút thêm ứng viên."
            if all_rejected
            else f"Hoàn tất. {result['passed']} CV hợp lệ, {result['rejected']} CV đã xóa."
        ),
    )


# ─────────────────────────────────────────────────────────────
# AHP ENDPOINTS
# ─────────────────────────────────────────────────────────────

@router.post(
    "/ahp/validate-matrix",
    response_model=AHPValidateResponse,
    summary="Kiểm tra Consistency Ratio của ma trận AHP",
    status_code=200,
)
def validate_ahp_matrix(
    body: AHPValidateRequest,
    current_user=Depends(require_hr_or_admin),
):
    """
    HR kéo thanh trượt → Frontend tính ma trận → Gửi lên để validate CR.

    - Nếu CR < 0.1: hợp lệ, trả về weights để preview
    - Nếu CR >= 0.1: HTTP 400, báo HR kéo lại
    """
    try:
        result = ahp_service.run_ahp(body.matrix, strict=True)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return AHPValidateResponse(
        is_consistent=result["is_consistent"],
        cr=result["consistency"]["cr"],
        ci=result["consistency"]["ci"],
        lambda_max=result["consistency"]["lambda_max"],
        weights=result["weights"],
        message=(
            f"✓ Ma trận nhất quán (CR={result['consistency']['cr']:.4f} < 0.1). Có thể chạy AHP."
        ),
    )


@router.post(
    "/ahp/config",
    response_model=AHPConfigSaveResponse,
    summary="Lưu cấu hình trọng số AHP cho 1 Vị trí (Job)",
    status_code=200,
)
def save_ahp_config(
    body: AHPConfigSaveRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr_or_admin),
):
    """
    HR lưu cấu hình AHP vĩnh viễn cho 1 Job.
    1. Kiểm tra Job tồn tại
    2. Validate Matrix CR < 0.1
    3. Lưu json weights vào DB
    """
    from app.models.job import CongViec
    
    job = db.query(CongViec).filter(CongViec.id == str(body.job_id)).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job không tồn tại")
        
    try:
        result = ahp_service.run_ahp(body.matrix, strict=True)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
        
    # Lưu weights + matrix gốc vào Job (để FE khôi phục thanh trượt)
    weights = result["weights"]
    job.ahp_weights = {"weights": weights, "matrix": body.matrix}
    db.commit()
    
    action_logger.info(
        "AHP_CONFIG_SAVED | job_id=%s | hr=%s | weights=%s",
        job.id, current_user.id, weights
    )
    
    return AHPConfigSaveResponse(
        job_id=body.job_id,
        is_consistent=result["is_consistent"],
        weights=weights,
        consistency=result["consistency"],
        message="Lưu cấu hình AHP thành công"
    )

@router.post(
    "/ahp/rank",
    response_model=AHPResponse,
    summary="Chạy AHP xếp hạng ứng viên dựa trên cấu hình đã lưu",
    status_code=200,
)
def run_ahp_rank(
    body: AHPRankRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_hr_or_admin),
):
    """
    HR bấm nút 'Chấm điểm' -> Lấy ahp_weights đã lưu -> Rank.
    """
    action_logger.info(
        "AHP_RANK_START | job_id=%s | hr=%s",
        body.job_id, current_user.id,
    )

    try:
        result = ahp_service.run_ahp_rank_only(
            db=db,
            job_id=str(body.job_id),
            hr_user_id=str(current_user.id),
        )
    except ValueError as e:
        err_str = str(e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=err_str,
        )

    return AHPResponse(
        job_id=body.job_id,
        top_10=result["top_10"],
        reserve_20=result["reserve_20"],
        total_ranked=result["total_ranked"],
        weights=result["weights"],
        consistency=None, # Not modifying consistency here, as it's just ranking
        message=(
            f"Đã xếp hạng {result['total_ranked']} ứng viên. "
            f"Top {len(result['top_10'])} + {len(result['reserve_20'])} dự bị."
        ),
    )
