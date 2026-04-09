# Hướng dẫn Cài đặt và Chạy Dự án (AI Recruitment System)

Tài liệu này hướng dẫn chi tiết các bước để thiết lập và khởi chạy hệ thống Tuyển dụng AI.

---

## 1. Yêu cầu hệ thống (Prerequisites)

Trước khi bắt đầu, hãy đảm bảo máy tính của bạn đã cài đặt:
- **Python:** Phiên bản 3.9 trở lên.
- **Node.js:** Phiên bản 18.x trở lên.
- **PostgreSQL:** Đã cài đặt và đang chạy (Cần tạo sẵn database tên `ai_recruitment`).

---

## 2. Thiết lập Backend (FastAPI)

Di chuyển vào thư mục Backend:
```bash
cd Project/Backend
```

### Bước 2.1: Tạo môi trường ảo (Virtual Environment)
```bash
python -m venv venv
# Kích hoạt trên Windows:
.\venv\Scripts\activate
# Kích hoạt trên macOS/Linux:
source venv/bin/activate
```

### Bước 2.2: Cài đặt các thư viện phụ thuộc
```bash
pip install -r requirements.txt
```

### Bước 2.3: Cấu hình biến môi trường (.env)
Tạo tệp `.env` trong thư mục `Project/Backend/` (hoặc chỉnh sửa tệp có sẵn) với nội dung:
```env
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/ai_recruitment
JWT_SECRET_KEY=your_super_secret_key_here
SUPER_ADMIN_EMAIL=admin@company.com
SUPER_ADMIN_PASSWORD=admin123
```
*Lưu ý: Thay `YOUR_PASSWORD` bằng mật khẩu Postgres của bạn.*

### Bước 2.4: Huấn luyện mô hình AI (Random Forest)
Dự án cần một file model đã được huấn luyện để lọc CV rác. Chạy lệnh sau:
```bash
python train_rf_model.py
```
Lệnh này sẽ tạo file `app/ai_models/rf_model.joblib`.

### Bước 2.5: Khởi chạy Backend
```bash
uvicorn app.main:app --reload
```
Backend sẽ chạy tại: `http://localhost:8000`

---

## 3. Thiết lập Frontend (Next.js)

Mở một terminal mới và di chuyển vào thư mục Frontend:
```bash
cd Project/frontend
```

### Bước 3.1: Cài đặt các gói npm
```bash
npm install
```

### Bước 3.2: Khởi chạy Frontend
```bash
npm run dev
```
Frontend sẽ chạy tại: `http://localhost:3000`

---

## 4. Tài khoản đăng nhập mặc định

Sau khi hệ thống khởi chạy, bạn có thể đăng nhập bằng tài khoản quản trị sau:
- **Email:** `admin@company.com`
- **Password:** `admin123` (Hoặc mật khẩu bạn đã thiết lập trong `.env`)

---

## 5. Các tính năng chính và cách dùng

### 5.1. Cổng ứng viên — Nộp hồ sơ (`/candidate/apply`)
*   Ứng viên chọn vị trí, điền thông tin và upload **CV (PDF)**.
*   **Chống Spam:** Hệ thống chặn trùng lặp tuyệt đối qua Email và nội dung file (MD5 Hash).

### 5.2. Cổng ứng viên — Tra cứu tiến độ (`/candidate/status`)
*   Tra cứu toàn bộ trạng thái hồ sơ chỉ với **Email** (Đã nộp → Vào vòng trong → Kết quả).

### 5.3. Dashboard HR (`/dashboard`)
*   Quản lý Chiến dịch, Vị trí tuyển dụng, xem nội dung CV trực tiếp và xuất báo cáo Excel.

### 5.4. Luồng AHP (Xếp hạng thông minh)
*   **Cấu hình:** HR so sánh tầm quan trọng của các tiêu chí để lấy trọng số.
*   **Xếp hạng:** AI tự động chấm điểm và hiển thị biểu đồ Radar, biểu đồ cột so sánh Top ứng viên.

### 5.5. Admin Portal (`/dashboard/admin/audit`)
*   Xem nhật ký hệ thống (Audit log) để theo dõi các thao tác của người dùng.

### 5.6. Mồi dữ liệu Test (Seed Data)

Hệ thống cung cấp 2 script chính để chuẩn bị dữ liệu kiểm thử:

#### 1. Khởi tạo cấu trúc (Chiến dịch & Job mẫu)
Lệnh này tạo sẵn các danh mục, chiến dịch và vị trí tuyển dụng mẫu:
```bash
cd Project/Backend
python seed_test_data.py
```

#### 2. nộp hàng loạt 20 CV thực tế (`Project/Backend/20_cv_mau`)
Sử dụng script này để nộp 20 file PDF có sẵn vào một Job cụ thể:
```bash
cd Project/Backend
python seed_real_cvs.py --job_id <UUID_CỦA_JOB>
```
*   **Cách lấy Job ID:** Đăng nhập Dashboard, vào chi tiết một Job, copy UUID trên thanh địa chỉ.
*   **Cơ chế:** Tự động sinh thông tin ứng viên tiếng Việt, kiểm tra trùng lặp Hash và chạy AI lọc rác ngay khi nộp.

---

## 6. Xử lý sự cố thường gặp

*   **Lỗi Database:** Đảm bảo PostgreSQL đã chạy và database `ai_recruitment` đã được tạo.
*   **Lỗi AI Model:** Nếu thiếu file model, hãy chạy `python train_rf_model.py`.
*   **Lỗi trùng hồ sơ:** Nếu thấy thông báo "Email đã nộp" hoặc "File CV này đã nộp", đó là tính năng chống spam. Hãy dùng Email khác hoặc File khác để test.
*   **Lỗi PDF Extraction:** Cài đặt `Visual C++ Redistributable` trên Windows nếu gặp lỗi thư viện `pdfplumber`.

---

