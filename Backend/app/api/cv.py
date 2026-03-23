# ============================================================
# app/routers/cv.py
# Router: /api/cv
# ============================================================
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.application import UploadCVResponse
from app.services import cv_service, export_service
from app.models.application import TrangThaiDon, DonUngTuyen
from app.models.candidate import UngVien
from app.middleware.auth_middleware import get_current_user
from app.models.user import NguoiDung
import uuid
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/cv", tags=["CV Upload"])

class TrackCandidateRequest(BaseModel):
    email: EmailStr

# ─────────────────────────────────────────────────────────────
# Mới: API Lấy danh sách Job động (Cho Dropdown Frontend)
# ─────────────────────────────────────────────────────────────
@router.get("/jobs", summary="Lấy danh sách các công việc đang mở")
def get_active_jobs(db: Session = Depends(get_db)):
    from app.models.job import CongViec, TrangThaiCongViec
    jobs = db.query(CongViec).filter(CongViec.trang_thai == TrangThaiCongViec.dang_mo).all()
    return [{"id": str(j.id), "tieu_de": j.tieu_de, "vi_tri": j.vi_tri} for j in jobs]


@router.post(
    "/upload",
    response_model=UploadCVResponse,
    summary="Ứng viên nộp CV",
    status_code=201,
)
async def upload_cv(
    request: Request,
    job_id: str = Form(..., description="UUID của tin tuyển dụng"),
    candidate_email: str = Form(...),
    candidate_name: str = Form(...),
    candidate_phone: str = Form(None),
    file: UploadFile = File(..., description="File PDF, tối đa 5MB, 5 trang"),
    db: Session = Depends(get_db),
):
    """
    Endpoint công khai (không cần JWT) — ứng viên tự nộp CV.
    Tích hợp toàn bộ: PDF Bomb check, Anti-Spam (MD5), lưu file.
    """
    from app.utils.file_utils import get_file_hash

    # ── Bước 1: Kiểm tra Content-Type (Friendly UX) ─────────
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Chỉ chấp nhận tệp định dạng PDF. Vui lòng kiểm tra lại tệp tin của bạn.",
        )

    # ── Bước 2: Kiểm tra Kích thước file (5MB limit) ───────
    # Đọc content để lấy size và hash
    content = await file.read()
    file_size = len(content)
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Tệp PDF của bạn vượt quá 5MB. Vui lòng nén nhỏ lại trước khi nộp.",
        )

    # ── Bước 3: Kiểm tra Email và Job ID (1 Email 1 Job 1 Lần) ──────────────
    existing_candidate = db.query(UngVien).filter(
        UngVien.email == candidate_email,
        UngVien.id_cong_viec == job_id
    ).first()
    
    if existing_candidate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email của bạn đã nộp cho vị trí hiện tại rồi. Vui lòng không nộp trùng lặp nhé!",
        )

    # ── Bước 4: Kiểm tra Trùng lặp Nội dung File (Anti-Spam Hash) ───────────
    file_hash = get_file_hash(content)
    existing_file = db.query(DonUngTuyen).filter(
        DonUngTuyen.ma_hash_cv == file_hash,
        DonUngTuyen.id_cong_viec == job_id
    ).first()

    if existing_file:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Hồ sơ (File CV) này đã được nộp cho vị trí hiện tại. Vui lòng không nộp trùng lặp tệp tin nhé!",
        )

    # Reset file pointer để service có thể đọc lại (nếu cần) hoặc truyền content qua service
    # Ở đây service hiện tại đang dùng UploadFile, nên cần seek(0)
    await file.seek(0)

    ip = request.client.host if request.client else "unknown"
    don = await cv_service.upload_cv(
        db=db,
        file=file,
        job_id=job_id,
        candidate_email=candidate_email,
        candidate_name=candidate_name,
        candidate_phone=candidate_phone,
        ip=ip,
    )

    # ── MỚI: Chạy RF ngay lập tức để phản hồi Real-time ───────
    from app.services import rf_service
    from app.models.job import CongViec
    from app.models.position import ViTri
    
    # Lấy vị trí để RF bám sát Job
    job = db.query(CongViec).filter(CongViec.id == job_id).first()
    position = None
    if job:
        position_obj = db.query(ViTri).filter(ViTri.id == job.id_vi_tri).first()
        if position_obj:
            position = position_obj.ma

    # don_id để trả về ngay cả khi bị xóa
    don_id = str(don.id)
    
    # Run RF pipeline (nếu fail -> don bị xóa trong DB)
    rf_res = rf_service.run_rf_pipeline(db, don, position=position)
    
    if rf_res.get("prediction") == 0:
        return UploadCVResponse(
            don_id=don_id,
            message="Rất tiếc, hồ sơ của bạn không phù hợp với yêu cầu vị trí hoặc bị hệ thống AI đánh giá là không hợp lệ (Spam).",
            trang_thai=TrangThaiDon.khong_phu_hop,
        )

    return UploadCVResponse(
        don_id=don_id,
        message="Nộp CV thành công. Hệ thống đã chấp nhận hồ sơ của bạn!",
        trang_thai=TrangThaiDon.da_nhan,
    )

@router.get(
    "/status/{app_id}",
    summary="Tra cứu trạng thái CV",
    status_code=200,
)
async def get_cv_status(
    app_id: str,
    db: Session = Depends(get_db),
):
    """Lấy trạng thái hồ sơ dựa trên ID đơn ứng tuyển."""
    try:
        don_uuid = uuid.UUID(app_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="ID không hợp lệ")

    don_record = db.query(DonUngTuyen, UngVien).join(UngVien, DonUngTuyen.id_ung_vien == UngVien.id).filter(DonUngTuyen.id == don_uuid).first()
    
    if not don_record:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ")
        
    don, uv = don_record
    return {
        "don_id": str(don.id),
        "candidate_name": uv.ho_ten,
        "trang_thai": don.trang_thai
    }

@router.post("/track", summary="Ứng viên tra cứu trạng thái")
async def track_candidate(
    req: TrackCandidateRequest,
    db: Session = Depends(get_db)
):
    """Tra cứu tất cả trạng thái của 1 email."""
    from app.models.job import CongViec

    results = db.query(DonUngTuyen, UngVien, CongViec).join(
        UngVien, DonUngTuyen.id_ung_vien == UngVien.id
    ).join(
        CongViec, DonUngTuyen.id_cong_viec == CongViec.id
    ).filter(
        UngVien.email == req.email
    ).all()

    if not results:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ nào khớp với Email này.")

    return [
        {
            "id": str(don.id),
            "candidate_name": uv.ho_ten,
            "job_title": job.tieu_de,
            "trang_thai": don.trang_thai,
            "ngay_nop": don.ngay_nop,
            "diem_ahp": don.diem_ahp if don.diem_ahp else 0.0
        }
        for don, uv, job in results
    ]

@router.get("/export/{job_id}", summary="Xuất báo cáo tuyển dụng (HR Only)")
async def export_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user)
):
    """Xuất kết quả Job ra Excel."""
    from app.models.job import CongViec
    
    job = db.query(CongViec).filter(CongViec.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Không tìm thấy Job")

    try:
        excel_stream = export_service.export_job_results_to_excel(db, job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo báo cáo: {str(e)}")
    
    # vi_tri is a relationship object, access .ten for name
    position_name = job.vi_tri.ten if job.vi_tri else "Unknown"
    filename = f"Ket_Qua_Tuyen_Dung_{position_name}_{job_id[:8]}.xlsx"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
