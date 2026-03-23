# ============================================================
# app/services/cv_service.py
# Business logic: Upload CV (PDF Bomb check + Anti-Spam + Lưu file)
# ============================================================
import os
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile, status
from app.core.config import get_settings
from app.core.logger import action_logger, error_logger
from app.models.candidate import UngVien
from app.models.application import DonUngTuyen, TrangThaiDon
from app.models.job import CongViec, TrangThaiCongViec
from app.middleware.pdf_guard import validate_and_hash_pdf
from app.services import audit_service

settings = get_settings()


async def upload_cv(
    db: Session,
    file: UploadFile,
    job_id: str,
    candidate_email: str,
    candidate_name: str,
    candidate_phone: str | None,
    ip: str = "unknown",
) -> DonUngTuyen:
    """
    Luồng upload CV đầy đủ:
    1. PDF Bomb Protection (size + pages)
    2. Anti-Spam (MD5 hash check)
    3. Lưu file vào storage/
    4. Tạo/link ứng viên trong DB
    5. Tạo đơn ứng tuyển ở trạng thái 'dang_cho'
    """
    # ── Bước 1: Validate PDF + lấy bytes + hash ──────────
    raw_bytes, md5_hash = await validate_and_hash_pdf(file)

    # ── Bước 2: Anti-Spam — kiểm tra trùng hash ──────────
    duplicate = db.query(DonUngTuyen).filter(
        DonUngTuyen.ma_hash_cv == md5_hash,
        DonUngTuyen.id_cong_viec == job_id,
    ).first()
    if duplicate:
        action_logger.info(
            "DUPLICATE_CV | hash=%s | email=%s | job_id=%s",
            md5_hash, candidate_email, job_id,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CV này đã được nộp trước đó. Vui lòng không nộp trùng lặp.",
        )

    # ── Bước 3: Kiểm tra job tồn tại và đang mở ─────────
    job = db.query(CongViec).filter(
        CongViec.id == job_id,
        CongViec.trang_thai == TrangThaiCongViec.dang_mo,
    ).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vị trí tuyển dụng không tồn tại hoặc đã đóng.",
        )

    # ── Bước 4: Lưu file vào disk ────────────────────────
    os.makedirs(settings.CV_UPLOAD_DIR, exist_ok=True)
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = os.path.join(settings.CV_UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as f:
        f.write(raw_bytes)

    # ── Bước 5: Upsert Ứng viên (Gắn với Job ID để dễ xóa theo đợt) ──
    candidate = db.query(UngVien).filter(
        UngVien.email == candidate_email,
        UngVien.id_cong_viec == job_id
    ).first()

    if not candidate:
        candidate = UngVien(
            id=uuid.uuid4(),
            email=candidate_email,
            ho_ten=candidate_name,
            so_dien_thoai=candidate_phone,
            id_cong_viec=job_id,
        )
        db.add(candidate)
        db.flush()  # Cần ID trước khi tạo đơn

    # ── Bước 6: Tạo đơn ứng tuyển ────────────────────────
    don = DonUngTuyen(
        id=uuid.uuid4(),
        id_ung_vien=candidate.id,
        id_cong_viec=job_id,
        duong_dan_cv=file_path,
        ma_hash_cv=md5_hash,
        trang_thai=TrangThaiDon.dang_cho,
    )
    db.add(don)
    db.commit()
    db.refresh(don)

    action_logger.info(
        "CV_UPLOADED | don_id=%s | candidate=%s | job_id=%s | hash=%s | IP=%s",
        don.id, candidate_email, job_id, md5_hash, ip,
    )
    return don


def hard_delete_cv(db: Session, don: DonUngTuyen, reason: str = "RF_REJECT") -> None:
    """
    Hard Delete: Xóa file vật lý + Xóa bản ghi trong DB.
    Được gọi bởi AI Pipeline (Phase 2) khi RF predict = 0 (Rác).
    """
    file_path = don.duong_dan_cv
    don_id = don.id
    candidate_id = don.id_ung_vien
    md5_hash = don.ma_hash_cv

    # 1. Xóa file vật lý
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            action_logger.info("PHYSICAL_FILE_DELETED | path=%s", file_path)
        except OSError as e:
            error_logger.error("Cannot delete CV file %s: %s", file_path, str(e))

    # 2. Xóa bản ghi đơn ứng tuyển
    db.delete(don)
    
    # 3. Kiểm tra và xóa ứng viên nếu không còn đơn nào khác (để sạch DB)
    # Trong logic hiện tại, UngVien gắn chặt với Job ID, nên thường 1-1.
    remaining_don = db.query(DonUngTuyen).filter(
        DonUngTuyen.id_ung_vien == candidate_id,
        DonUngTuyen.id != don_id
    ).first()
    
    if not remaining_don:
        candidate = db.query(UngVien).filter(UngVien.id == candidate_id).first()
        if candidate:
            db.delete(candidate)
            action_logger.info("CANDIDATE_RECORD_DELETED | candidate_id=%s", candidate_id)

    db.commit()

    # ── GHI AUDIT LOG ───────────────────────────────────────
    # Format: 'AI_HARD_DELETE | MD5: ...'
    if reason == "RF_REJECT":
        audit_description = f"AI_HARD_DELETE | MD5: {md5_hash}"
        audit_action = "AI_HARD_DELETE"
    else:
        audit_description = f"JOB_HARD_DELETE | MD5: {md5_hash} | Reason: {reason}"
        audit_action = "HARD_DELETE"

    audit_service.log_action(
        db,
        user_id=None,  # System-triggered
        action=audit_action,
        details=audit_description
    )

    action_logger.info(
        "HARD_DELETE_COMPLETE | don_id=%s | reason=%s", don_id, reason
    )
