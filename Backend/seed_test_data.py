import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.campaign import ChienDich, TrangThaiChienDich
from app.models.position import ViTri
from app.models.job import CongViec, TrangThaiCongViec
from app.models.user import NguoiDung

def seed_data():
    db: Session = SessionLocal()
    try:
        # Get admin
        admin = db.query(NguoiDung).filter(NguoiDung.email == 'admin@company.com').first()
        if not admin:
            print("Admin not found!")
            return

        # 1. Create Positions
        it_pos = ViTri(id=uuid.uuid4(), ten="Lập trình viên", ma="IT_Intern", mo_ta="Lập trình viên")
        mkt_pos = ViTri(id=uuid.uuid4(), ten="Marketing", ma="Marketing_Intern", mo_ta="NV Marketing")
        db.add_all([it_pos, mkt_pos])
        db.commit()

        # 2. Create Campaign
        campaign = ChienDich(
            id=uuid.uuid4(),
            tieu_de="Tuyển dụng tháng 3/2026",
            mo_ta="Đợt tuyển lớn nhất năm",
            ngay_bat_dau=datetime.now(timezone.utc),
            ngay_ket_thuc=datetime.now(timezone.utc) + timedelta(days=30),
            trang_thai=TrangThaiChienDich.dang_mo,
            creator_id=admin.id
        )
        db.add(campaign)
        db.commit()

        # 3. Create Jobs
        job1 = CongViec(
            id=uuid.uuid4(),
            tieu_de="Thực tập sinh Lập trình (IT Intern)",
            id_vi_tri=it_pos.id,
            campaign_id=campaign.id,
            creator_id=admin.id,
            trang_thai=TrangThaiCongViec.dang_mo
        )
        job2 = CongViec(
            id=uuid.uuid4(),
            tieu_de="Thực tập sinh Marketing",
            id_vi_tri=mkt_pos.id,
            campaign_id=campaign.id,
            creator_id=admin.id,
            trang_thai=TrangThaiCongViec.dang_mo
        )
        db.add_all([job1, job2])
        db.commit()

        print("Seed success!")

    finally:
        db.close()

if __name__ == '__main__':
    seed_data()
