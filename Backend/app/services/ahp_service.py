# ============================================================
# app/services/ahp_service.py
# AHP (Analytic Hierarchy Process) Service
# Nhận Pairwise Comparison Matrix → Tính trọng số tiêu chí → Xếp hạng ứng viên
# STRICT MODE: Bắt buộc CR < 0.1, ném ValueError nếu vi phạm
# ============================================================
import numpy as np
from typing import Optional
from sqlalchemy.orm import Session

from app.core.logger import action_logger, error_logger

# ─────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────

# 4 tiêu chí đánh giá (theo PROJECT_SPEC)
CRITERIA = [
    "ky_thuat",    # Kỹ thuật / Technical skills
    "hoc_van",     # Học vấn / Education
    "ngoai_ngu",   # Ngoại ngữ / Language
    "tich_cuc",    # Tích cực / Attitude / Soft skills
]

# Random Index (RI) — bảng Saaty cho n=1..10
# Index = n-1 (tức RI_TABLE[3] = RI cho n=4)
RI_TABLE = {
    1: 0.00,
    2: 0.00,
    3: 0.58,
    4: 0.90,   # <-- n=4 cho 4 tiêu chí
    5: 1.12,
    6: 1.24,
    7: 1.32,
    8: 1.41,
    9: 1.45,
    10: 1.49,
}

CR_THRESHOLD = 0.1  # Ngưỡng CR tối đa (theo business rule)

# Số lượng top ứng viên lấy ra
TOP_N = 10
RESERVE_N = 20


# ─────────────────────────────────────────────────────────────
# CORE AHP MATH FUNCTIONS (có Unit Test cho các hàm này)
# ─────────────────────────────────────────────────────────────

def validate_matrix_input(matrix: list[list[float]]) -> np.ndarray:
    """
    Kiểm tra tính hợp lệ của ma trận đầu vào trước khi xử lý:
    - Phải là ma trận vuông n×n
    - Đường chéo chính phải = 1
    - a[i][j] = 1 / a[j][i] (reciprocal property, tolerance 1e-6)
    - Tất cả giá trị phải dương

    Raises:
        ValueError: nếu ma trận không hợp lệ
    Returns:
        np.ndarray: ma trận đã validated
    """
    mat = np.array(matrix, dtype=float)
    n = mat.shape[0]

    if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
        raise ValueError(f"Ma trận phải vuông n×n, nhận được shape={mat.shape}")

    if n < 2:
        raise ValueError("Ma trận phải có ít nhất 2×2")

    # Kiểm tra tất cả dương
    if np.any(mat <= 0):
        raise ValueError("Tất cả phần tử ma trận phải dương (> 0)")

    # Kiểm tra đường chéo = 1
    for i in range(n):
        if abs(mat[i, i] - 1.0) > 1e-9:
            raise ValueError(
                f"Đường chéo chính phải = 1 (vị trí [{i},{i}] = {mat[i,i]})"
            )

    # Kiểm tra tính đảo nghịch (reciprocal: a[i][j] * a[j][i] ≈ 1)
    for i in range(n):
        for j in range(i + 1, n):
            product = mat[i, j] * mat[j, i]
            if abs(product - 1.0) > 1e-6:
                raise ValueError(
                    f"Vi phạm reciprocal property tại [{i},{j}]: "
                    f"a[{i}][{j}] × a[{j}][{i}] = {product:.6f} (phải = 1.0)"
                )

    return mat


def compute_priority_vector(matrix: np.ndarray) -> np.ndarray:
    """
    Tính Priority Vector (trọng số tiêu chí) bằng phương pháp
    Geometric Mean (chuẩn hóa từng hàng theo căn bậc n).

    Formula:
        w_i = (∏_j a_ij)^(1/n) / Σ_k (∏_j a_kj)^(1/n)

    Args:
        matrix: np.ndarray vuông n×n đã validated

    Returns:
        np.ndarray shape (n,): priority vector (tổng = 1.0)
    """
    n = matrix.shape[0]
    # Geometric mean của mỗi hàng
    geometric_means = np.zeros(n)
    for i in range(n):
        geometric_means[i] = np.prod(matrix[i, :]) ** (1.0 / n)

    # Normalize
    total = geometric_means.sum()
    if total == 0:
        raise ValueError("Geometric mean tổng bằng 0 — ma trận không hợp lệ")

    priority_vector = geometric_means / total
    return priority_vector


def compute_consistency_ratio(matrix: np.ndarray, priority_vector: np.ndarray) -> dict:
    """
    Tính Consistency Ratio (CR) theo công thức Saaty.

    Steps:
    1. λ_max = trung bình của (weighted sum vector / priority vector)
    2. CI = (λ_max - n) / (n - 1)
    3. CR = CI / RI[n]

    Args:
        matrix: Ma trận so sánh cặp n×n
        priority_vector: Priority vector đã tính

    Returns:
        dict với: lambda_max, ci, ri, cr
    """
    n = matrix.shape[0]

    # Weighted sum vector: Aw (matrix × priority_vector)
    weighted_sum = matrix @ priority_vector

    # λ_max: average of ratios
    ratios = weighted_sum / priority_vector
    lambda_max = float(np.mean(ratios))

    # CI
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0

    # RI
    ri = RI_TABLE.get(n, 1.49)

    # CR
    cr = ci / ri if ri > 0 else 0.0

    return {
        "lambda_max": round(lambda_max, 6),
        "ci": round(ci, 6),
        "ri": round(ri, 4),
        "cr": round(cr, 6),
    }


def run_ahp(
    matrix: list[list[float]],
    strict: bool = True,
) -> dict:
    """
    Chạy toàn bộ AHP pipeline:
    1. Validate matrix
    2. Tính priority vector
    3. Tính CR
    4. Nếu strict=True và CR > 0.1 → ném ValueError

    Args:
        matrix: Ma trận so sánh cặp (list of lists)
        strict: Bật Strict Mode (CR < 0.1 bắt buộc)

    Returns:
        dict với:
            - weights: dict {criteria_name: weight_value}
            - priority_vector: list[float]
            - consistency: dict {lambda_max, ci, ri, cr}
            - is_consistent: bool

    Raises:
        ValueError: nếu matrix không hợp lệ hoặc CR >= 0.1 (strict mode)
    """
    # Step 1: Validate
    mat = validate_matrix_input(matrix)
    n = mat.shape[0]

    if n != len(CRITERIA):
        raise ValueError(
            f"Ma trận phải {len(CRITERIA)}×{len(CRITERIA)} (4 tiêu chí: {CRITERIA}), "
            f"nhận được {n}×{n}"
        )

    # Step 2: Priority Vector
    priority_vector = compute_priority_vector(mat)

    # Step 3: Consistency
    consistency = compute_consistency_ratio(mat, priority_vector)
    cr = consistency["cr"]
    is_consistent = cr < CR_THRESHOLD

    # Step 4: Strict Mode check
    if strict and not is_consistent:
        raise ValueError(
            f"Consistency Ratio CR={cr:.4f} vượt ngưỡng {CR_THRESHOLD}. "
            f"Vui lòng điều chỉnh lại ma trận so sánh."
        )

    # Build weights dict
    weights = {
        criteria: round(float(priority_vector[i]), 6)
        for i, criteria in enumerate(CRITERIA)
    }

    return {
        "weights": weights,
        "priority_vector": [round(float(v), 6) for v in priority_vector],
        "consistency": consistency,
        "is_consistent": is_consistent,
    }


# ─────────────────────────────────────────────────────────────
# CANDIDATE SCORING FUNCTIONS
# ─────────────────────────────────────────────────────────────

def score_candidate(
    candidate_scores: dict[str, float],
    weights: dict[str, float],
) -> float:
    """
    Tính điểm AHP cuối cùng cho 1 ứng viên.

    Formula: score = Σ (weight_i × raw_score_i)

    Args:
        candidate_scores: {criteria_name: score} — điểm thô (0-10)
        weights: {criteria_name: weight} — trọng số từ AHP

    Returns:
        float: điểm tổng hợp (weighted sum)
    """
    total = 0.0
    for criteria, weight in weights.items():
        raw_score = candidate_scores.get(criteria, 0.0)
        total += weight * float(raw_score)
    return round(total, 4)


def rank_candidates(
    candidates: list[dict],
    weights: dict[str, float],
) -> list[dict]:
    """
    Xếp hạng danh sách ứng viên theo điểm AHP.
    Logic giải quyết trùng điểm: Ưu tiên tiêu chí có trọng số cao nhất.

    Args:
        candidates: list of dict, mỗi dict có:
            - don_id: UUID của đơn ứng tuyển
            - candidate_name: Tên ứng viên
            - scores: {criteria: raw_score}
        weights: trọng số từ AHP output

    Returns:
        Danh sách ứng viên đã xếp hạng, mỗi item thêm:
            - ahp_score: float
            - rank: int (1-based)
    """
    # 1. Tính điểm AHP cho từng ứng viên
    for candidate in candidates:
        candidate["ahp_score"] = score_candidate(
            candidate.get("scores", {}), weights
        )

    # 2. Xác định tiêu chí quan trọng nhất để phá băng (tie-break)
    highest_weight_criterion = max(weights, key=weights.get)

    # 3. Sắp xếp giảm dần: ahp_score trước, sau đó là điểm của tiêu chí quan trọng nhất
    ranked = sorted(
        candidates,
        key=lambda x: (x["ahp_score"], x["scores"].get(highest_weight_criterion, 0)),
        reverse=True
    )

    for i, c in enumerate(ranked):
        c["rank"] = i + 1

    return ranked


def run_ahp_batch(
    db: Session,
    job_id: str,
    pairwise_matrix: list[list[float]],
    hr_user_id: str,
) -> dict:
    """
    Chạy toàn bộ AHP pipeline cho 1 job:
    1. Validate và tính AHP weights từ pairwise_matrix
    2. Lấy tất cả đơn đã pass RF (trang_thai='da_nhan') của job_id
    3. Tính điểm AHP từ keyword features của mỗi CV
    4. Cập nhật diem_ahp vào DB
    5. Đồng bộ ahp_weights vào Job Model (Persistence)
    6. Trả về Top 10 + 20 dự bị

    Ngoại lệ: Nếu 100% CV bị RF reject (không có CV pass), ném ValueError.

    Args:
        db: SQLAlchemy Session
        job_id: UUID string của job
        pairwise_matrix: 4×4 AHP matrix từ HR
        hr_user_id: UUID của HR đang chạy (để audit log)

    Returns:
        dict với top_10, reserve_20, weights, consistency
    """
    from app.models.application import DonUngTuyen, TrangThaiDon
    from app.models.candidate import UngVien
    from app.models.job import CongViec

    # ── Bước 1: Tính AHP weights ─────────────────────────────
    try:
        ahp_result = run_ahp(pairwise_matrix, strict=True)
    except ValueError as e:
        error_logger.warning("AHP_CR_FAIL | job_id=%s | hr=%s | %s", job_id, hr_user_id, str(e))
        raise

    weights = ahp_result["weights"]
    
    # Đồng bộ ahp_weights vào Job (Sticky Settings) - nested format
    job = db.query(CongViec).filter(CongViec.id == job_id).first()
    if job:
        job.ahp_weights = {"weights": weights, "matrix": pairwise_matrix}
        db.commit()

    action_logger.info(
        "AHP_WEIGHTS | job_id=%s | hr=%s | weights=%s | CR=%.4f",
        job_id, hr_user_id, weights, ahp_result["consistency"]["cr"],
    )

    # ── Bước 2: Lấy đơn đã pass RF ───────────────────────────
    passed_applications = db.query(DonUngTuyen).filter(
        DonUngTuyen.id_cong_viec == job_id,
        DonUngTuyen.trang_thai == TrangThaiDon.da_nhan,
    ).all()

    if not passed_applications:
        raise ValueError(
            "Không có ứng viên nào qua vòng lọc RF. "
            "Tất cả CV đã bị đánh là không phù hợp."
        )

    # ── Bước 3: Tính điểm AHP cho mỗi ứng viên ──────────────
    candidates_data = []
    for don in passed_applications:
        # Đọc CV để trích xuất feature làm điểm thô
        scores = _compute_candidate_raw_scores(don)

        candidate = db.query(UngVien).filter(UngVien.id == don.id_ung_vien).first()
        candidate_name = candidate.ho_ten if candidate else "Unknown"

        candidates_data.append({
            "don_id": str(don.id),
            "candidate_name": candidate_name,
            "candidate_id": str(don.id_ung_vien),
            "scores": scores,
        })

    # ── Bước 4: Xếp hạng ─────────────────────────────────────
    ranked = rank_candidates(candidates_data, weights)

    # ── Bước 5: Cập nhật diem_ahp vào DB ─────────────────────
    don_map = {str(don.id): don for don in passed_applications}
    for c in ranked:
        don = don_map.get(c["don_id"])
        if don:
            don.diem_ahp = c["ahp_score"]
    db.commit()

    # ── Bước 6: Tách Top 10 + 20 dự bị ──────────────────────
    top_10 = ranked[:TOP_N]
    reserve_20 = ranked[TOP_N : TOP_N + RESERVE_N]

    action_logger.info(
        "AHP_BATCH_DONE | job_id=%s | hr=%s | total=%d | top10=%d | reserve=%d",
        job_id, hr_user_id, len(ranked), len(top_10), len(reserve_20),
    )

    return {
        "top_10": top_10,
        "reserve_20": reserve_20,
        "total_ranked": len(ranked),
        "weights": weights,
        "consistency": ahp_result["consistency"],
    }


def run_ahp_rank_only(
    db: Session,
    job_id: str,
    hr_user_id: str,
) -> dict:
    """
    Xếp hạng ứng viên dựa trên ahp_weights đã lưu sẵn trong Job.
    Không cần truyền pairwise_matrix. Lấy weights từ DB.
    
    Ngoại lệ:
    - Chưa cấu hình AHP weights → ValueError
    - Không có ứng viên pass RF → ValueError
    """
    from app.models.application import DonUngTuyen, TrangThaiDon
    from app.models.candidate import UngVien
    from app.models.job import CongViec

    # ── Lấy Job và kiểm tra ahp_weights ──────────────────────
    job = db.query(CongViec).filter(CongViec.id == job_id).first()
    if not job:
        raise ValueError(f"Không tìm thấy Job id={job_id}")
    
    if not job.ahp_weights:
        raise ValueError(
            "Chưa cấu hình trọng số AHP cho vị trí này. "
            "Vui lòng vào Tab 'Cấu hình AHP' để thiết lập và lưu trọng số trước."
        )
    
    weights_data = job.ahp_weights  # dict hoặc {weights: {...}, matrix: [...]}
    # Backward compatible: nếu có key "weights" thì lấy, không thì dùng trực tiếp
    if isinstance(weights_data, dict) and "weights" in weights_data:
        weights = weights_data["weights"]
    else:
        weights = weights_data  # format cũ: flat dict {criteria: weight}

    # ── Lấy đơn đã pass RF ───────────────────────────────────
    passed_applications = db.query(DonUngTuyen).filter(
        DonUngTuyen.id_cong_viec == job_id,
        DonUngTuyen.trang_thai == TrangThaiDon.da_nhan,
    ).all()

    if not passed_applications:
        raise ValueError(
            "Không có ứng viên nào qua vòng lọc RF. "
            "Tất cả CV đã bị đánh là không phù hợp."
        )

    # ── Tính điểm AHP cho mỗi ứng viên ──────────────────────
    candidates_data = []
    for don in passed_applications:
        scores = _compute_candidate_raw_scores(don)
        candidate = db.query(UngVien).filter(UngVien.id == don.id_ung_vien).first()
        candidate_name = candidate.ho_ten if candidate else "Unknown"
        candidates_data.append({
            "don_id": str(don.id),
            "candidate_name": candidate_name,
            "candidate_id": str(don.id_ung_vien),
            "scores": scores,
        })

    # ── Xếp hạng ─────────────────────────────────────────────
    ranked = rank_candidates(candidates_data, weights)

    # ── Cập nhật diem_ahp vào DB ─────────────────────────────
    don_map = {str(don.id): don for don in passed_applications}
    for c in ranked:
        don = don_map.get(c["don_id"])
        if don:
            don.diem_ahp = c["ahp_score"]
    db.commit()

    top_10 = ranked[:TOP_N]
    reserve_20 = ranked[TOP_N : TOP_N + RESERVE_N]

    action_logger.info(
        "AHP_RANK_ONLY_DONE | job_id=%s | hr=%s | total=%d",
        job_id, hr_user_id, len(ranked),
    )

    return {
        "top_10": top_10,
        "reserve_20": reserve_20,
        "total_ranked": len(ranked),
        "weights": weights,
    }


def _compute_candidate_raw_scores(don: "DonUngTuyen") -> dict[str, float]:
    """
    Tính điểm thô (0-10) cho 4 tiêu chí AHP bằng Keyword Matching từ nlp_service.
    """
    from app.services.nlp_service import (
        extract_text_from_pdf, calculate_raw_scores
    )

    if not don.duong_dan_cv or not __import__("os").path.exists(don.duong_dan_cv):
        return {c: 0.0 for c in CRITERIA}

    with open(don.duong_dan_cv, "rb") as f:
        pdf_bytes = f.read()

    text = extract_text_from_pdf(pdf_bytes)
    return calculate_raw_scores(text)
