# ============================================================
# app/core/logger.py
# Module Logging: 2 luồng độc lập action.log & error.log
# ============================================================
import logging
import os
from logging.handlers import RotatingFileHandler
from app.core.config import get_settings

settings = get_settings()

# Đảm bảo thư mục logs tồn tại
os.makedirs(settings.LOG_DIR, exist_ok=True)

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _build_file_handler(filename: str, level: int) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        os.path.join(settings.LOG_DIR, filename),
        maxBytes=10 * 1024 * 1024,  # 10 MB mỗi file
        backupCount=5,
        encoding="utf-8",
    )
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    return handler


def _build_console_handler(level: int) -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    return handler


# ── ACTION LOGGER ─────────────────────────────────────────
# Ghi lại mọi thao tác của HR: đăng nhập, chạy AHP, xóa CV...
action_logger = logging.getLogger("action")
action_logger.setLevel(logging.INFO)
action_logger.propagate = False
action_logger.addHandler(_build_file_handler("action.log", logging.INFO))
action_logger.addHandler(_build_console_handler(logging.INFO))

# ── ERROR LOGGER ──────────────────────────────────────────
# Ghi lại lỗi hệ thống / lỗi toán học (AHP, RF, DB, v.v.)
error_logger = logging.getLogger("error")
error_logger.setLevel(logging.WARNING)
error_logger.propagate = False
error_logger.addHandler(_build_file_handler("error.log", logging.WARNING))
error_logger.addHandler(_build_console_handler(logging.WARNING))
