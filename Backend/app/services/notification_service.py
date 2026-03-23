# ============================================================
# app/services/notification_service.py
# Business logic: Quản lý thông báo (Notifications)
# ============================================================
from typing import List
from sqlalchemy.orm import Session
from app.models.notification import NhatKyThongBao


def create_notification(
    db: Session,
    user_id: str,
    content: str,
    type: str,
) -> NhatKyThongBao:
    """
    Tạo thông báo mới cho người dùng.
    """
    notification = NhatKyThongBao(
        id_nguoi_dung=user_id,
        noi_dung=content,
        loai=type,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_unread_notifications(
    db: Session,
    user_id: str,
) -> List[NhatKyThongBao]:
    """
    Lấy danh sách thông báo chưa đọc của người dùng.
    """
    return (
        db.query(NhatKyThongBao)
        .filter(
            NhatKyThongBao.id_nguoi_dung == user_id,
            NhatKyThongBao.da_doc == False,
        )
        .all()
    )


def mark_as_read(
    db: Session,
    notification_id: int,
) -> NhatKyThongBao:
    """
    Đánh dấu thông báo là đã đọc.
    """
    notification = (
        db.query(NhatKyThongBao)
        .filter(NhatKyThongBao.id == notification_id)
        .first()
    )
    if notification:
        notification.da_doc = True
        db.commit()
        db.refresh(notification)
    return notification
