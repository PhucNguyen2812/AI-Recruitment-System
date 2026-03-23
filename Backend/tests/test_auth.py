# ============================================================
# tests/test_auth.py
# Unit tests cho Authentication API
# ============================================================
import pytest
from fastapi.testclient import TestClient
from app.core.config import get_settings

settings = get_settings()


class TestLogin:
    def test_login_success_admin(self, client: TestClient):
        """Admin đăng nhập thành công, nhận được access_token."""
        resp = client.post("/api/auth/login", json={
            "email": settings.SUPER_ADMIN_EMAIL,
            "mat_khau": settings.SUPER_ADMIN_PASSWORD,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["vai_tro"] == "quan_tri_vien"

    def test_login_wrong_password(self, client: TestClient):
        """Mật khẩu sai → 401."""
        resp = client.post("/api/auth/login", json={
            "email": settings.SUPER_ADMIN_EMAIL,
            "mat_khau": "WrongPassword",
        })
        assert resp.status_code == 401

    def test_login_unknown_email(self, client: TestClient):
        """Email không tồn tại → 401."""
        resp = client.post("/api/auth/login", json={
            "email": "ghost@company.com",
            "mat_khau": settings.SUPER_ADMIN_PASSWORD,
        })
        assert resp.status_code == 401

    def test_login_invalid_email_format(self, client: TestClient):
        """Email sai format → 422 Validation Error."""
        resp = client.post("/api/auth/login", json={
            "email": "not-an-email",
            "mat_khau": settings.SUPER_ADMIN_PASSWORD,
        })
        assert resp.status_code == 422


class TestCreateHR:
    def test_create_hr_success(self, client: TestClient, auth_headers: dict):
        """Admin tạo tài khoản HR thành công."""
        resp = client.post("/api/auth/create-hr", json={
            "email": "hr1@company.com",
            "mat_khau": "HRPass@123",
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "hr1@company.com"
        assert data["vai_tro"] == "nhan_su"

    def test_create_hr_duplicate_email(self, client: TestClient, auth_headers: dict):
        """Email HR trùng → 409 Conflict."""
        payload = {"email": "hr2@company.com", "mat_khau": "HRPass@123"}
        client.post("/api/auth/create-hr", json=payload, headers=auth_headers)
        resp = client.post("/api/auth/create-hr", json=payload, headers=auth_headers)
        assert resp.status_code == 409

    def test_create_hr_without_auth(self, client: TestClient):
        """Không có JWT → 403."""
        resp = client.post("/api/auth/create-hr", json={
            "email": "hr_no_auth@company.com",
            "mat_khau": "HRPass@123",
        })
        assert resp.status_code in (401, 403)

    def test_hr_cannot_create_hr(self, client: TestClient, auth_headers: dict):
        """HR không được tạo tài khoản HR khác."""
        # Tạo HR trước
        client.post("/api/auth/create-hr", json={
            "email": "hr_test@company.com",
            "mat_khau": "HRPass@123",
        }, headers=auth_headers)

        # HR login
        hr_resp = client.post("/api/auth/login", json={
            "email": "hr_test@company.com",
            "mat_khau": "HRPass@123",
        })
        hr_token = hr_resp.json()["access_token"]
        hr_headers = {"Authorization": f"Bearer {hr_token}"}

        # HR thử tạo HR mới → 403
        resp = client.post("/api/auth/create-hr", json={
            "email": "hr_new@company.com",
            "mat_khau": "HRPass@123",
        }, headers=hr_headers)
        assert resp.status_code == 403


class TestHealthCheck:
    def test_health_ok(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
