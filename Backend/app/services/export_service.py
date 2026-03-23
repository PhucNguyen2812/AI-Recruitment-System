# ============================================================
# app/services/export_service.py
# Export results to Excel/CSV for HR Analysis
# ============================================================
import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session
from app.models.application import DonUngTuyen, TrangThaiDon
from app.models.candidate import UngVien
from app.models.job import CongViec
from app.services.ahp_service import _compute_candidate_raw_scores
import os

def export_job_results_to_excel(db: Session, job_id: str) -> BytesIO:
    """
    Xuất danh sách ứng viên của 1 Job ra file Excel (.xlsx)
    Bao gồm: Họ tên, Email, SĐT, Điểm RF, Điểm AHP, Chi tiết tiêu chí.
    """
    # 1. Truy vấn dữ liệu
    results = db.query(DonUngTuyen, UngVien, CongViec).join(
        UngVien, DonUngTuyen.id_ung_vien == UngVien.id
    ).join(
        CongViec, DonUngTuyen.id_cong_viec == CongViec.id
    ).filter(DonUngTuyen.id_cong_viec == job_id).all()

    if not results:
        # Trả về file trống nếu không có dữ liệu
        df_empty = pd.DataFrame(columns=[
            "Họ tên", "Email", "Số điện thoại", "Trạng thái", 
            "Điểm RF", "Điểm AHP", "Kỹ thuật", "Học vấn", "Ngoại ngữ", "Tích cực"
        ])
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_empty.to_excel(writer, index=False, sheet_name='No Data')
        output.seek(0)
        return output

    # 2. Chuẩn bị dữ liệu cho DataFrame
    data = []
    for don, uv, job in results:
        # Lấy điểm chi tiết (nếu file CV còn tồn tại)
        detailed_scores = {
            "ky_thuat": 0.0, "hoc_van": 0.0, "ngoai_ngu": 0.0, "tich_cuc": 0.0
        }
        
        # Nếu đã pass RF và file còn đó, tính lại điểm chi tiết để export
        if don.trang_thai != TrangThaiDon.khong_phu_hop and don.duong_dan_cv and os.path.exists(don.duong_dan_cv):
            try:
                detailed_scores = _compute_candidate_raw_scores(don)
            except Exception:
                pass # Fallback to 0.0 if error during extraction
        
        data.append({
            "Họ tên": uv.ho_ten,
            "Email": uv.email,
            "Số điện thoại": uv.so_dien_thoai or "N/A",
            "Trạng thái": don.trang_thai.value,
            "Điểm RF": "Đạt" if don.diem_rf == 1 else "Không đạt",
            "Điểm AHP": round(don.diem_ahp, 4) if don.diem_ahp is not None else 0.0,
            "Kỹ thuật": detailed_scores.get("ky_thuat", 0.0),
            "Học vấn": detailed_scores.get("hoc_van", 0.0),
            "Ngoại ngữ": detailed_scores.get("ngoai_ngu", 0.0),
            "Tích cực": detailed_scores.get("tich_cuc", 0.0),
        })

    # 3. Tạo DataFrame và xuất ra BytesIO
    df = pd.DataFrame(data)
    
    # Sắp xếp theo điểm AHP giảm dần
    df = df.sort_values(by="Điểm AHP", ascending=False)

    output = BytesIO()
    # Sử dụng xlsxwriter (mặc định của pandas nếu đã cài)
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Ket_Qua_Tuyen_Dung')
        
        # Tự động điều chỉnh độ rộng cột (Auto-fit)
        worksheet = writer.sheets['Ket_Qua_Tuyen_Dung']
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
            worksheet.set_column(i, i, column_len)

    output.seek(0)
    return output
