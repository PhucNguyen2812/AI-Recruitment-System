# ============================================================
# tests/test_pdf_guard.py
# Unit tests cho PDF Bomb Protection & Anti-Spam
# ============================================================
import io
import hashlib
import pytest
from unittest.mock import patch, MagicMock
from fastapi import UploadFile
from app.middleware.pdf_guard import validate_and_hash_pdf
from app.core.config import get_settings

settings = get_settings()
MAX_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


def make_upload_file(content: bytes, content_type: str = "application/pdf", filename: str = "test.pdf") -> UploadFile:
    """Helper tạo UploadFile mock."""
    file = UploadFile(
        filename=filename,
        headers={"content-type": content_type},
    )
    # Override read() để trả về bytes đã định sẵn
    file.read = lambda n=-1: asyncio_return(content[:n] if n > 0 else content)
    file.content_type = content_type
    return file


import asyncio

def asyncio_return(value):
    async def coro():
        return value
    return coro()


class TestPDFGuard:
    @pytest.mark.asyncio
    async def test_wrong_content_type_rejected(self):
        """File không phải PDF bị chặn → HTTPException 415."""
        from fastapi import HTTPException
        file = MagicMock(spec=UploadFile)
        file.content_type = "text/plain"
        file.read = MagicMock(return_value=asyncio_return(b"hello"))

        with pytest.raises(HTTPException) as exc:
            await validate_and_hash_pdf(file)
        assert exc.value.status_code == 415

    @pytest.mark.asyncio
    async def test_oversized_file_rejected(self):
        """File > 5MB bị chặn → HTTPException 413."""
        from fastapi import HTTPException
        big_content = b"0" * (MAX_BYTES + 1)
        file = MagicMock(spec=UploadFile)
        file.content_type = "application/pdf"
        file.read = MagicMock(return_value=asyncio_return(big_content))

        with pytest.raises(HTTPException) as exc:
            await validate_and_hash_pdf(file)
        assert exc.value.status_code == 413

    @pytest.mark.asyncio
    async def test_invalid_pdf_rejected(self):
        """Nội dung không phải PDF hợp lệ → HTTPException 400."""
        from fastapi import HTTPException
        fake_pdf = b"not a real pdf content"
        file = MagicMock(spec=UploadFile)
        file.content_type = "application/pdf"
        file.read = MagicMock(return_value=asyncio_return(fake_pdf))

        with pytest.raises(HTTPException) as exc:
            await validate_and_hash_pdf(file)
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_md5_hash_computed_correctly(self):
        """MD5 hash được tính đúng từ nội dung file."""
        # Dùng minimal PDF hợp lệ (1 trang)
        minimal_pdf = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n9\n%%EOF"
        )
        expected_hash = hashlib.md5(minimal_pdf).hexdigest()

        file = MagicMock(spec=UploadFile)
        file.content_type = "application/pdf"
        file.read = MagicMock(return_value=asyncio_return(minimal_pdf))

        with patch("pdfplumber.open") as mock_pdf:
            mock_pdf.return_value.__enter__ = MagicMock(return_value=MagicMock(pages=[MagicMock()]))
            mock_pdf.return_value.__exit__ = MagicMock(return_value=False)
            _, actual_hash = await validate_and_hash_pdf(file)

        assert actual_hash == expected_hash


class TestMD5HashUniqueness:
    def test_different_files_different_hash(self):
        """2 file nội dung khác nhau → hash khác nhau."""
        h1 = hashlib.md5(b"content_a").hexdigest()
        h2 = hashlib.md5(b"content_b").hexdigest()
        assert h1 != h2

    def test_same_content_same_hash(self):
        """Cùng nội dung → hash giống nhau (anti-spam detection)."""
        content = b"same cv content"
        assert hashlib.md5(content).hexdigest() == hashlib.md5(content).hexdigest()

    def test_hash_length_is_32(self):
        """MD5 hash luôn dài 32 ký tự hex."""
        h = hashlib.md5(b"test").hexdigest()
        assert len(h) == 32
