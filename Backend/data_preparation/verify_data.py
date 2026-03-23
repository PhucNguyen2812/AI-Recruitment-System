"""
verify_data.py
Phase 0 — Data Verification Script
Đọc ngẫu nhiên 5 file PDF từ mỗi thư mục (relevant + irrelevant).
Trích xuất text bằng pdfplumber và in ra console để kiểm tra:
  - Text không rỗng
  - Không bị lỗi mã hoá
  - Nội dung đọc được, có keywords quan trọng
"""

import os
import random
import pdfplumber
import pandas as pd

# ─────────────────────────────────────────────
# PATH CONFIG
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "..", "dataset")
RELEVANT_DIR = os.path.join(DATASET_DIR, "raw_cvs", "relevant")
IRRELEVANT_DIR = os.path.join(DATASET_DIR, "raw_cvs", "irrelevant")
LABELS_PATH = os.path.join(DATASET_DIR, "labels.csv")

SAMPLE_SIZE = 5
MIN_TEXT_LENGTH = 50   # Số ký tự tối thiểu để file không bị coi là rỗng

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def extract_text_from_pdf(filepath: str) -> str:
    """Trích xuất toàn bộ text từ PDF bằng pdfplumber."""
    text_parts = []
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        return f"[ERROR extracting {filepath}]: {e}"


def check_file(filepath: str, label: str, idx: int) -> dict:
    """Kiểm tra một file PDF và trả về kết quả."""
    filename = os.path.basename(filepath)
    file_size_kb = os.path.getsize(filepath) / 1024
    text = extract_text_from_pdf(filepath)
    text_len = len(text.strip())
    has_error = text.startswith("[ERROR")
    is_empty = text_len < MIN_TEXT_LENGTH and not has_error

    status = "✓ PASS" if (not has_error and not is_empty) else "✗ FAIL"

    result = {
        "index": idx,
        "label": label,
        "filename": filename,
        "file_size_kb": round(file_size_kb, 2),
        "text_length": text_len,
        "has_error": has_error,
        "is_empty": is_empty,
        "status": status,
    }
    return result, text


def print_separator(char="─", width=70):
    print(char * width)


def sample_files(directory: str, n: int) -> list:
    """Lấy ngẫu nhiên n file PDF từ thư mục."""
    all_files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
    if len(all_files) == 0:
        return []
    return [os.path.join(directory, f) for f in random.sample(all_files, min(n, len(all_files)))]


# ─────────────────────────────────────────────
# MAIN VERIFICATION
# ─────────────────────────────────────────────
def main():
    random.seed(None)   # Fresh random seed mỗi lần chạy
    print_separator("=")
    print(" PHASE 0 — DATA VERIFICATION REPORT")
    print_separator("=")

    all_results = []
    failed_count = 0
    total_checked = 0

    # ─── 1. Check dataset directories exist ───
    print("\n[1] Checking directory structure...")
    dirs_ok = True
    for d, name in [(RELEVANT_DIR, "relevant"), (IRRELEVANT_DIR, "irrelevant")]:
        exists = os.path.isdir(d)
        count = len([f for f in os.listdir(d) if f.endswith(".pdf")]) if exists else 0
        status = "✓" if exists else "✗ MISSING"
        print(f"  {status} dataset/raw_cvs/{name}/ — {count} PDF files found")
        if not exists:
            dirs_ok = False
    if not dirs_ok:
        print("\n[ERROR] One or more directories missing. Run generate_cvs.py first.")
        return

    # ─── 2. Check labels.csv ───
    print("\n[2] Checking labels.csv...")
    if os.path.exists(LABELS_PATH):
        df = pd.read_csv(LABELS_PATH)
        n_relevant = (df["label"] == 1).sum()
        n_irrelevant = (df["label"] == 0).sum()
        print(f"  ✓ labels.csv found — {len(df)} total rows")
        print(f"    Relevant (label=1): {n_relevant}")
        print(f"    Irrelevant (label=0): {n_irrelevant}")
    else:
        print("  ✗ labels.csv NOT FOUND")

    # ─── 3. Sample and verify PDFs ───
    for label, directory in [("RELEVANT", RELEVANT_DIR), ("IRRELEVANT", IRRELEVANT_DIR)]:
        print_separator()
        print(f"\n[3] Sampling {SAMPLE_SIZE} {label} CVs...")
        print_separator()

        sample = sample_files(directory, SAMPLE_SIZE)
        if not sample:
            print(f"  [WARNING] No PDF files found in {directory}")
            continue

        for idx, filepath in enumerate(sample, 1):
            result, text = check_file(filepath, label, idx)
            all_results.append(result)
            total_checked += 1
            if result["has_error"] or result["is_empty"]:
                failed_count += 1

            print(f"\n  [{idx}] {result['status']} | {result['filename']}")
            print(f"       Size: {result['file_size_kb']} KB | Text length: {result['text_length']} chars")

            if result["has_error"]:
                print(f"       [ERROR] Extraction failed!")
            elif result["is_empty"]:
                print(f"       [WARNING] Text too short (< {MIN_TEXT_LENGTH} chars) — may be empty/corrupt")
            else:
                # Print first 300 chars of extracted text as preview
                preview = text.strip()[:300].replace("\n", " ")
                print(f"       Preview: {preview}...")

    # ─── 4. Summary ───
    print_separator("=")
    print(f"\n VERIFICATION SUMMARY")
    print_separator("=")
    print(f"  Total PDFs checked : {total_checked}")
    print(f"  Passed             : {total_checked - failed_count}")
    print(f"  Failed             : {failed_count}")

    if failed_count == 0:
        print(f"\n  ✓ ALL CHECKS PASSED — Data is ready for Phase 1 (AI Training).")
    else:
        print(f"\n  ✗ {failed_count} file(s) failed. Check generate_cvs.py configuration.")

    print_separator("=")
    print()


if __name__ == "__main__":
    main()
