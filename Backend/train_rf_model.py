#!/usr/bin/env python
# ============================================================
# train_rf_model.py
# Script train mô hình Random Forest từ dataset Phase 0.
# Chạy lệnh (từ thư mục Backend/):
#   python train_rf_model.py
# Output: app/ai_models/rf_model.joblib + feature_columns.json
# ============================================================
import os
import sys
import json
import logging

import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

# Thêm project root vào sys.path để import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.nlp_service import (
    extract_text_from_pdf,
    extract_features_for_rf,
    features_to_list,
    FEATURE_COLUMNS,
)

# ── Config ────────────────────────────────────────────────────
DATASET_DIR = os.path.join(os.path.dirname(__file__), "dataset", "raw_cvs")
LABELS_CSV = os.path.join(os.path.dirname(__file__), "dataset", "labels.csv")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "app", "ai_models")
MODEL_PATH = os.path.join(OUTPUT_DIR, "rf_model.joblib")
FEATURE_COLS_PATH = os.path.join(OUTPUT_DIR, "feature_columns.json")

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def load_dataset() -> tuple[list[list[float]], list[int]]:
    """
    Đọc labels.csv, bóc text từ từng PDF, trích xuất features.
    PDF nằm trong subdirectory: raw_cvs/relevant/ hoặc raw_cvs/irrelevant/
    Trả về (X, y) để train.
    """
    log.info("Đọc labels.csv từ: %s", LABELS_CSV)
    df = pd.read_csv(LABELS_CSV)
    log.info("  Tổng mẫu trong CSV: %d", len(df))

    X = []
    y = []
    skipped = 0

    for idx, row in df.iterrows():
        filename = str(row["filename"]).strip()
        label = int(row["label"])
        position = str(row.get("position", "")).strip()
        position = position if position != "None" and position else None

        # PDF nằm trong subdir theo label
        subdir = "relevant" if label == 1 else "irrelevant"
        pdf_path = os.path.join(DATASET_DIR, subdir, filename)

        if not os.path.exists(pdf_path):
            log.warning("  Không tìm thấy file: %s/%s — bỏ qua", subdir, filename)
            skipped += 1
            continue

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        text = extract_text_from_pdf(pdf_bytes)
        features = extract_features_for_rf(text, position=position)
        feature_vec = features_to_list(features)

        X.append(feature_vec)
        y.append(label)

        if (idx + 1) % 100 == 0:
            log.info("  Đã xử lý %d/%d samples...", idx + 1, len(df))

    log.info("Dataset: %d samples, bỏ qua %d file không tìm thấy", len(X), skipped)
    log.info("Phân phối nhãn: 0 (rác)=%d | 1 (hợp lệ)=%d",
             y.count(0), y.count(1))
    return X, y


def train_and_evaluate(X: list, y: list) -> RandomForestClassifier:
    """
    Train Random Forest với cross-validation, in metrics.
    """
    X_np = np.array(X)
    y_np = np.array(y)

    # Split 80/20
    X_train, X_test, y_train, y_test = train_test_split(
        X_np, y_np, test_size=0.2, random_state=42, stratify=y_np
    )
    log.info("Train: %d mẫu | Test: %d mẫu", len(X_train), len(X_test))

    # Model config: n_estimators=100 đủ tốt cho 1000 mẫu
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=None,            # Cho phép grow đủ sâu
        min_samples_split=5,       # Tránh overfitting
        min_samples_leaf=2,
        class_weight="balanced",   # Xử lý potential imbalance
        random_state=42,
        n_jobs=-1,                 # Dùng tất cả CPU cores
    )

    log.info("Bắt đầu train Random Forest...")
    clf.fit(X_train, y_train)

    # ── Evaluate ──────────────────────────────────────────────
    log.info("\n── CROSS-VALIDATION ──")
    cv_scores = cross_val_score(clf, X_np, y_np, cv=5, scoring="f1")
    log.info("F1 CV scores: %s", cv_scores.round(4))
    log.info("F1 CV mean: %.4f ± %.4f", cv_scores.mean(), cv_scores.std())

    log.info("\n── TEST SET EVALUATION ──")
    y_pred = clf.predict(X_test)
    log.info("\n%s", classification_report(y_test, y_pred,
             target_names=["Rác (0)", "Hợp lệ (1)"]))

    cm = confusion_matrix(y_test, y_pred)
    log.info("Confusion Matrix:\n%s", cm)

    # ── Feature Importance ────────────────────────────────────
    log.info("\n── FEATURE IMPORTANCE ──")
    importances = clf.feature_importances_
    for col, imp in sorted(zip(FEATURE_COLUMNS, importances), key=lambda x: -x[1]):
        log.info("  %-25s: %.4f", col, imp)

    return clf


def save_model(clf: RandomForestClassifier) -> None:
    """Lưu model và danh sách feature columns ra disk."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    joblib.dump(clf, MODEL_PATH)
    log.info("✓ Model lưu tại: %s", MODEL_PATH)

    with open(FEATURE_COLS_PATH, "w", encoding="utf-8") as f:
        json.dump(FEATURE_COLUMNS, f, indent=2)
    log.info("✓ Feature columns lưu tại: %s", FEATURE_COLS_PATH)


def main():
    log.info("=" * 60)
    log.info("RF MODEL TRAINING — AI Recruitment System")
    log.info("=" * 60)

    X, y = load_dataset()
    if len(X) < 10:
        log.error("Không đủ dữ liệu để train (< 10 mẫu). Kiểm tra dataset!")
        sys.exit(1)

    clf = train_and_evaluate(X, y)
    save_model(clf)

    log.info("\n✓ Training hoàn tất! Model sẵn sàng cho Phase 2.")


if __name__ == "__main__":
    main()
