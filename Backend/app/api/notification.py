# ============================================================
# app/routers/notification.py
# API endpoints for notification management
# ============================================================
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import NguoiDung
from app.services import notification_service
from app.schemas.notification import NotificationRead

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("", response_model=List[NotificationRead])
def list_unread_notifications(
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    """
    Returns unread notifications for the current user.
    """
    return notification_service.get_unread_notifications(db, user_id=str(current_user.id))

@router.patch("/{id}/read", response_model=NotificationRead)
def mark_notification_as_read(
    id: int,
    db: Session = Depends(get_db),
    current_user: NguoiDung = Depends(get_current_user),
):
    """
    Marks a notification as read.
    """
    from app.models.notification import NhatKyThongBao
    notification = db.query(NhatKyThongBao).filter(NhatKyThongBao.id == id).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thông báo không tồn tại."
        )
    
    # Security check: Ensure the notification belongs to the current user
    if str(notification.id_nguoi_dung) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền thực hiện hành động này."
        )
    
    return notification_service.mark_as_read(db, notification_id=id)
