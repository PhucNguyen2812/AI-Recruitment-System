import os
import pytest
import uuid
from sqlalchemy.orm import Session
from app.models.job import CongViec, TrangThaiCongViec
from app.models.application import DonUngTuyen, TrangThaiDon
from app.models.candidate import UngVien
from app.models.user import NguoiDung
from app.models.position import ViTri
from app.models.campaign import ChienDich
from app.models.audit_log import NhatKyHeThong
from app.services.job_service import close_job
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Setup test DB
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

def test_hard_delete_on_close_job(db: Session):
    # 1. Setup required entities
    user = NguoiDung(
        id=uuid.uuid4(),
        email="hr@example.com",
        ho_ten="HR Manager",
        mat_khau="hashed_password",
        role="admin"
    )
    db.add(user)
    
    vi_tri = ViTri(
        id=uuid.uuid4(),
        ten="IT Intern",
        ma="IT_Intern"
    )
    db.add(vi_tri)
    
    campaign = ChienDich(
        id=uuid.uuid4(),
        ten="Summer Intern 2024",
        trang_thai="dang_mo"
    )
    db.add(campaign)
    db.commit()

    # 2. Create a Job
    job = CongViec(
        id=uuid.uuid4(),
        tieu_de="Test Job",
        id_vi_tri=vi_tri.id,
        campaign_id=campaign.id,
        creator_id=user.id,
        trang_thai=TrangThaiCongViec.dang_mo
    )
    db.add(job)
    db.commit()

    # 3. Create a Candidate and Application with a dummy file
    candidate = UngVien(
        id=uuid.uuid4(),
        email="test@example.com",
        ho_ten="Test Candidate",
        id_cong_viec=job.id
    )
    db.add(candidate)
    db.commit()

    # Create dummy CV file
    cv_path = f"storage/cvs/test_{uuid.uuid4()}.pdf"
    os.makedirs("storage/cvs", exist_ok=True)
    with open(cv_path, "w") as f:
        f.write("dummy content")

    application = DonUngTuyen(
        id=uuid.uuid4(),
        id_ung_vien=candidate.id,
        id_cong_viec=job.id,
        duong_dan_cv=cv_path,
        ma_hash_cv="dummy_hash_123",
        trang_thai=TrangThaiDon.da_nhan
    )
    db.add(application)
    db.commit()

    # Verify setup
    assert os.path.exists(cv_path)
    assert db.query(DonUngTuyen).count() == 1
    assert db.query(UngVien).count() == 1

    # 4. Close the Job (Trigger Hard Delete)
    result = close_job(db, str(job.id))

    # 5. Verify results
    assert result is True
    
    # Check Job status
    db.refresh(job)
    assert job.trang_thai == TrangThaiCongViec.da_dong

    # Check File is deleted
    assert not os.path.exists(cv_path)

    # Check DB records are deleted (Privacy compliance)
    assert db.query(DonUngTuyen).filter(DonUngTuyen.id_cong_viec == job.id).count() == 0
    assert db.query(UngVien).filter(UngVien.id_cong_viec == job.id).count() == 0

    # Check Audit Log for Job Closing
    audit_close = db.query(NhatKyHeThong).filter(NhatKyHeThong.hanh_dong == "CLOSE_JOB").first()
    assert audit_close is not None
    assert str(job.id) in audit_close.chi_tiet

    # Check Audit Log for Hard Delete (The new part!)
    audit_hard_delete = db.query(NhatKyHeThong).filter(
        NhatKyHeThong.hanh_dong == "HARD_DELETE"
    ).first()
    assert audit_hard_delete is not None
    assert "JOB_HARD_DELETE" in audit_hard_delete.chi_tiet
    assert "dummy_hash_123" in audit_hard_delete.chi_tiet
