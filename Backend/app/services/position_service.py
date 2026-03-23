# ============================================================
# app/services/position_service.py
# Service layer for Position business logic 
# ============================================================
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.position import ViTri
from app.schemas.position import PositionCreate, PositionUpdate
from app.core.types import GUID


def get_positions(db: Session, skip: int = 0, limit: int = 100) -> List[ViTri]:
    return db.query(ViTri).order_by(ViTri.ngay_tao.desc()).offset(skip).limit(limit).all()


def get_position_by_id(db: Session, position_id: GUID) -> Optional[ViTri]:
    return db.query(ViTri).filter(ViTri.id == position_id).first()


def get_position_by_code(db: Session, code: str) -> Optional[ViTri]:
    return db.query(ViTri).filter(ViTri.ma == code).first()


def create_position(db: Session, position: PositionCreate) -> ViTri:
    db_position = ViTri(**position.model_dump())
    db.add(db_position)
    db.commit()
    db.refresh(db_position)
    return db_position


def update_position(db: Session, db_position: ViTri, position_update: PositionUpdate) -> ViTri:
    update_data = position_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_position, key, value)
    
    db.commit()
    db.refresh(db_position)
    return db_position


def delete_position(db: Session, db_position: ViTri) -> None:
    db.delete(db_position)
    db.commit()
