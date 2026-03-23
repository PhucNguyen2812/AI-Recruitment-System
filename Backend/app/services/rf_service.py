# ============================================================
# app/services/rf_service.py
# Random Forest Service: Load model, predict CV, Hard Delete rác
# ============================================================
import os
import logging
from functools import lru_cache

import joblib
import numpy as np
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.nlp_service import (
    extract_text_from_pdf,
    extract_features_for_rf,
    features_to_list,
)
from app.models.application import DonUngTuyen, TrangThaiDon
from app.core.logger import action_logger, error_logger

logger = logging.getLogger("error")
settings = get_settings()

# ── Path đến model ─────────────────────────────────────────
_MODEL_PATH = os.path.join(settings.AI_MODEL_DIR, "rf_model.joblib")


@lru_cache(maxsize=1)
def _load_model():
    """
    Load RF model từ disk — chỉ load 1 lần (lru_cache).
    Ném RuntimeError nếu model chưa được train.
    """
    if not os.path.exists(_MODEL_PATH):
        raise RuntimeError(
            f"RF model chưa được train. Chạy: python train_rf_model.py\n"
            f"Model path: {_MODEL_PATH}"
        )
    model = joblib.load(_MODEL_PATH)
    action_logger.info("RF model loaded from: %s", _MODEL_PATH)
    return model


def predict_cv(pdf_bytes: bytes, position: str | None = None) -> dict:
    """
    Predict một CV có phải CV hợp lệ hay không.

    Args:
        pdf_bytes: Nội dung file PDF dạng bytes
        position: Vị trí ứng tuyển (IT_Intern / Marketing_Intern)

    Returns:
        dict với:
            - prediction: int (1=hợp lệ, 0=rác)
            - probability: float (confidence score của class 1)
            - text_length: int (để debug)
            - keyword_count: int (để debug)
            - language: str (en/vi)
    """
    # Bước 1: Bóc text
    text = extract_text_from_pdf(pdf_bytes)

    # Bước 2: Trích xuất features
    features = extract_features_for_rf(text, position=position)
    feature_vec = features_to_list(features)

    # Edge case: CV hoàn toàn rỗng (0 words) → Rác ngay
    if features["total_words"] == 0:
        error_logger.warning(
            "RF predict: empty text — auto classify as trash (position=%s)", position
        )
        return {
            "prediction": 0,
            "probability": 0.0,
            "text_length": 0,
            "keyword_count": 0,
            "language": "unknown",
        }

    # Bước 3: Load model và predict
    clf = _load_model()
    X = np.array([feature_vec])
    prediction = int(clf.predict(X)[0])
    probabilities = clf.predict_proba(X)[0]  # [prob_class_0, prob_class_1]
    probability = float(probabilities[1]) if len(probabilities) > 1 else float(probabilities[0])

    # Detect language for response
    from app.services.nlp_service import detect_language
    lang = detect_language(text)

    return {
        "prediction": prediction,
        "probability": round(probability, 4),
        "text_length": features["text_length"],
        "keyword_count": features["keyword_count"],
        "language": lang,
    }


def run_rf_pipeline(
    db: Session,
    don: DonUngTuyen,
    position: str | None = None,
) -> dict:
    """
    Chạy toàn bộ pipeline RF cho 1 đơn ứng tuyển:
    1. Đọc file PDF từ disk
    2. Predict bằng RF model
    3. Nếu predict=0 (rác) → Hard Delete file + cập nhật DB
    4. Nếu predict=1 (hợp lệ) → Update diem_rf=1, trang_thai='da_nhan'

    Returns:
        dict kết quả predict
    """
    result = {"don_id": str(don.id), "error": None}

    # Đọc file PDF
    if not don.duong_dan_cv or not os.path.exists(don.duong_dan_cv):
        error_logger.error(
            "RF pipeline: file CV không tồn tại | don_id=%s | path=%s",
            don.id, don.duong_dan_cv,
        )
        result["error"] = "File CV không tồn tại trên disk."
        result["prediction"] = -1
        return result

    with open(don.duong_dan_cv, "rb") as f:
        pdf_bytes = f.read()

    # Predict
    try:
        pred_result = predict_cv(pdf_bytes, position=position)
    except RuntimeError as e:
        error_logger.error("RF pipeline error: %s", str(e))
        result["error"] = str(e)
        result["prediction"] = -1
        return result

    prediction = pred_result["prediction"]
    result.update(pred_result)

    # Cập nhật DB
    don.diem_rf = prediction

    if prediction == 0:
        # ── HARD DELETE ──────────────────────────────────────
        _hard_delete_file_and_update_db(db, don)
        action_logger.info(
            "RF_REJECT | don_id=%s | prob=%.4f | lang=%s | keywords=%d",
            don.id, pred_result["probability"],
            pred_result["language"], pred_result["keyword_count"],
        )
    else:
        # ── PASS ─────────────────────────────────────────────
        don.trang_thai = TrangThaiDon.da_nhan
        db.commit()
        action_logger.info(
            "RF_PASS | don_id=%s | prob=%.4f | lang=%s | keywords=%d",
            don.id, pred_result["probability"],
            pred_result["language"], pred_result["keyword_count"],
        )

    return result


def _hard_delete_file_and_update_db(db: Session, don: DonUngTuyen) -> None:
    """
    Hard Delete: Xóa file vật lý + Xóa bản ghi trong DB.
    Được gọi khi RF xác định CV là rác.
    """
    from app.services.cv_service import hard_delete_cv
    hard_delete_cv(db, don, reason="RF_REJECT")


def run_rf_batch(
    db: Session,
    job_id: str,
    position: str | None = None,
) -> dict:
    """
    Chạy RF pipeline cho TẤT CẢ đơn ứng tuyển đang chờ (trang_thai='dang_cho')
    của một job_id cụ thể.

    Returns:
        dict thống kê: total, passed, rejected, errors
    """
    from app.models.application import DonUngTuyen, TrangThaiDon

    pending_applications = db.query(DonUngTuyen).filter(
        DonUngTuyen.id_cong_viec == job_id,
        DonUngTuyen.trang_thai == TrangThaiDon.dang_cho,
    ).all()

    total = len(pending_applications)
    if total == 0:
        return {
            "total": 0,
            "passed": 0,
            "rejected": 0,
            "errors": 0,
            "message": "Không có đơn nào đang chờ xử lý.",
        }

    passed = 0
    rejected = 0
    errors = 0

    for don in pending_applications:
        result = run_rf_pipeline(db, don, position=position)
        if result.get("error"):
            errors += 1
        elif result.get("prediction") == 1:
            passed += 1
        else:
            rejected += 1

    # ── Ngoại lệ: 100% CV là rác ─────────────────────────────
    if passed == 0 and errors == 0:
        action_logger.warning(
            "RF_BATCH_ALL_REJECTED | job_id=%s | total=%d | rejected=%d",
            job_id, total, rejected,
        )

    action_logger.info(
        "RF_BATCH_DONE | job_id=%s | total=%d | passed=%d | rejected=%d | errors=%d",
        job_id, total, passed, rejected, errors,
    )

    return {
        "total": total,
        "passed": passed,
        "rejected": rejected,
        "errors": errors,
    }
