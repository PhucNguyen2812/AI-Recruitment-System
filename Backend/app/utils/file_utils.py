# ============================================================
# app/utils/file_utils.py
# Tiện ích xử lý file
# ============================================================
import hashlib


def get_file_hash(file_content: bytes) -> str:
    """
    Tính toán MD5 hash của nội dung file.
    Dùng để phát hiện trùng lặp CV.
    """
    return hashlib.md5(file_content).hexdigest()
