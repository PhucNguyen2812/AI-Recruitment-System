# ============================================================
# tests/test_cv_api.py
# Unit tests cho CV Upload & Status API
# ============================================================
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os
import uuid
from app.models.job import CongViec, TrangThaiCongViec
from app.models.application import DonUngTuyen, TrangThaiDon

@pytest.fixture
def test_job(client: TestClient) -> CongViec:
    """Fixture tạo test job giả để ứng viên có chỗ nộp CV."""
    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()
    job = CongViec(
        id=str(uuid.uuid4()),
        tieu_de="Test IT Intern",
        vi_tri="IT_Intern",
        mo_ta="Mô tả công việc",
        trang_thai=TrangThaiCongViec.dang_mo
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    db.close()
    return job

class TestCVAPI:
    def test_upload_cv_success(self, client: TestClient, test_job: CongViec, tmp_path: Path, monkeypatch):
        """Giả lập upload một file PDF hợp lệ nhỏ."""
        # Patch setting để upload vào thư mục tạm
        import app.services.cv_service as cv_service_module
        monkeypatch.setattr(cv_service_module.settings, "CV_UPLOAD_DIR", str(tmp_path))

        # Helper tạo file pdf giả lập (cần magic payload %PDF)
        file_content = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n9\n%%EOF"
        )
        
        resp = client.post(
            "/api/cv/upload",
            data={
                "candidate_name": "Test Candidate",
                "candidate_email": "test@candidate.com",
                "candidate_phone": "0912345678",
                "job_id": str(test_job.id)
            },
            files={"file": ("test.pdf", file_content, "application/pdf")}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "don_id" in data
        assert data["trang_thai"] == "dang_cho"
        assert data["message"] == "Nộp CV thành công. Hệ thống sẽ xử lý và thông báo kết quả."

    def test_upload_duplicate_hash(self, client: TestClient, test_job: CongViec, tmp_path: Path, monkeypatch):
        """Nộp 2 lần cùng một file -> Lỗi 409 Conflict"""
        import app.services.cv_service as cv_service_module
        monkeypatch.setattr(cv_service_module.settings, "CV_UPLOAD_DIR", str(tmp_path))

        file_content = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n9\n%%EOF"
        )
        payload = {
            "candidate_name": "Dup Candidate",
            "candidate_email": "dup@candidate.com",
            "job_id": str(test_job.id)
        }

        # Nộp lần 1 -> Thành công
        r1 = client.post("/api/cv/upload", data=payload, files={"file": ("dup.pdf", file_content, "application/pdf")})
        assert r1.status_code == 201

        # Nộp lần 2 -> 409
        r2 = client.post("/api/cv/upload", data=payload, files={"file": ("dup.pdf", file_content, "application/pdf")})
        assert r2.status_code == 409
        assert "trùng lặp" in r2.json()["detail"].lower()

    def test_get_application_status(self, client: TestClient, test_job: CongViec, tmp_path: Path, monkeypatch):
        """Test tra cứu status của hồ sơ bằng ID"""
        import app.services.cv_service as cv_service_module
        monkeypatch.setattr(cv_service_module.settings, "CV_UPLOAD_DIR", str(tmp_path))

        file_content = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n9\n%%EOF"
        )
        r1 = client.post(
            "/api/cv/upload", 
            data={"candidate_name": "Status Candidate", "candidate_email": "st@candidate.com", "job_id": str(test_job.id)},
            files={"file": ("st.pdf", file_content, "application/pdf")}
        )
        assert r1.status_code == 201
        app_id = r1.json()["don_id"]

        r_status = client.get(f"/api/cv/status/{app_id}")
        assert r_status.status_code == 200
        data = r_status.json()
        assert data["candidate_name"] == "Status Candidate"
        assert data["trang_thai"] == "dang_cho" # 'dang_cho' maps to 'submitted' in frontend API

    def test_get_application_status_not_found(self, client: TestClient):
        """Tra cứu ID bậy -> 404"""
        r = client.get(f"/api/cv/status/12345678-1234-1234-1234-123456789abc")
        assert r.status_code == 404
