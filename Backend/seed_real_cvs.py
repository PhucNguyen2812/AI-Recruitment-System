import os
import uuid
import argparse
from dotenv import load_dotenv
from faker import Faker
from fastapi.testclient import TestClient

# Import app để dùng TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.candidate import UngVien
from app.models.job import CongViec

load_dotenv()

fake = Faker('vi_VN')
CV_DIR = "20_cv_mau"

def check_already_applied(db, email, job_id):
    """Kiểm tra ứng viên đã nộp cho Job này chưa"""
    return db.query(UngVien).filter(
        UngVien.email == email,
        UngVien.id_cong_viec == job_id
    ).first() is not None

def main():
    parser = argparse.ArgumentParser(description="Seed 20 real CVs from folder to a specific Job.")
    parser.add_argument("--job_id", type=str, required=True, help="UUID của Job cần nộp CV")
    args = parser.parse_args()

    if not os.path.exists(CV_DIR):
        print(f"Error: Thư mục {CV_DIR} không tồn tại."); return

    # Lấy danh sách file PDF và sắp xếp
    cv_files = sorted([f for f in os.listdir(CV_DIR) if f.lower().endswith('.pdf')])
    if not cv_files:
        print(f"Error: Không tìm thấy file PDF nào trong {CV_DIR}."); return
    
    # Giới hạn 20 file đầu tiên (nếu có nhiều hơn)
    cv_files = cv_files[:20]

    db = SessionLocal()
    # Kiểm tra Job ID hợp lệ
    job = db.query(CongViec).filter(CongViec.id == args.job_id).first()
    if not job:
        print(f"Error: Job ID {args.job_id} không tồn tại trong Database."); db.close(); return

    print(f"=== Đang nộp 20 CV thực tế cho vị trí: {job.tieu_de} ===")
    
    client = TestClient(app)
    count = 0

    for filename in cv_files:
        name = fake.name()
        # Tạo email cố định dựa trên tên hoặc index để dễ quản lý nhưng vẫn đảm bảo duy nhất
        email = f"candidate_{count+1}_{uuid.uuid4().hex[:4]}@example.com"
        phone = fake.phone_number().replace(" ", "").replace(".", "")[:11]
        filepath = os.path.join(CV_DIR, filename)

        # Kiểm tra trùng lặp (trường hợp chạy lại script)
        if check_already_applied(db, email, args.job_id):
            print(f"  [Bỏ qua] {email} đã nộp cho Job này.")
            continue

        try:
            with open(filepath, "rb") as pdf_file:
                response = client.post(
                    "/api/cv/upload",
                    data={
                        "candidate_name": name,
                        "candidate_email": email,
                        "candidate_phone": phone,
                        "job_id": args.job_id
                    },
                    files={"file": (filename, pdf_file, "application/pdf")}
                )
            
            if response.status_code == 200:
                print(f"  [Thành công] {count+1}/20: {name} - File: {filename}")
                count += 1
            else:
                print(f"  [Lỗi {response.status_code}] {filename}: {response.json().get('detail')}")
        except Exception as e:
            print(f"  [Exception] {filename}: {str(e)}")

    db.close()
    print(f"\nHoàn tất! Đã nộp thành công {count} CV.")

if __name__ == "__main__":
    main()
