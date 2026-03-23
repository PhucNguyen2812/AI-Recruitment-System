# ============================================================
# app/middleware/pdf_guard.py
# PDF Bomb Protection Middleware
# Chặn file không phải PDF, > 5MB, > 5 trang
# ============================================================
import hashlib
from fastapi import UploadFile, HTTPException, status
import pdfplumber
import io
from app.core.config import get_settings
from app.core.logger import error_logger

settings = get_settings()

MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


async def validate_and_hash_pdf(file: UploadFile) -> tuple[bytes, str]:
    """
    Đọc file upload, kiểm tra:
      1. Content-Type phải là application/pdf
      2. Kích thước < 5MB
      3. Số trang PDF < 5 trang
    Trả về (file_bytes, md5_hash) nếu hợp lệ.
    Ném HTTPException nếu vi phạm.
    """
    # ── Bước 1: Check content type ────────────────────────
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Chỉ chấp nhận file PDF.",
        )

    # ── Bước 2: Đọc raw bytes (giới hạn MAX_BYTES + 1 để detect vượt quá)
    raw = await file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        error_logger.warning(
            "PDF upload rejected: size=%d bytes (limit=%d MB)",
            len(raw),
            settings.MAX_FILE_SIZE_MB,
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File vượt quá {settings.MAX_FILE_SIZE_MB}MB.",
        )

    # ── Bước 3: Kiểm tra số trang PDF ────────────────────
    try:
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            num_pages = len(pdf.pages)
    except Exception as e:
        error_logger.error("Cannot open PDF: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File PDF không hợp lệ hoặc bị lỗi.",
        )

    if num_pages > settings.MAX_PDF_PAGES:
        error_logger.warning(
            "PDF upload rejected: pages=%d (limit=%d)", num_pages, settings.MAX_PDF_PAGES
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"PDF vượt quá {settings.MAX_PDF_PAGES} trang (hiện có {num_pages} trang).",
        )

    # ── Bước 4: Tính MD5 Hash ─────────────────────────────
    md5_hash = hashlib.md5(raw).hexdigest()

    return raw, md5_hash
