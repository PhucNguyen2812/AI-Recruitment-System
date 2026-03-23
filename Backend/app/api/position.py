# ============================================================
# app/api/position.py
# API router for Position Operations
# ============================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.position import PositionCreate, PositionUpdate, PositionResponse
from app.services import position_service
from app.middleware.auth_middleware import get_current_user
from app.models.user import NguoiDung

router = APIRouter(prefix="/api/positions", tags=["Positions"])


@router.get("/", response_model=List[PositionResponse])
def get_positions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return position_service.get_positions(db, skip=skip, limit=limit)


@router.post("/", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
def create_position(position: PositionCreate, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    # Check if position code exists
    db_position = position_service.get_position_by_code(db, code=position.ma)
    if db_position:
        raise HTTPException(status_code=400, detail="Position code already registered")
    return position_service.create_position(db=db, position=position)


@router.get("/{position_id}", response_model=PositionResponse)
def get_position(position_id: str, db: Session = Depends(get_db)):
    db_position = position_service.get_position_by_id(db, position_id=position_id)
    if not db_position:
        raise HTTPException(status_code=404, detail="Position not found")
    return db_position


@router.put("/{position_id}", response_model=PositionResponse)
def update_position(position_id: str, position_update: PositionUpdate, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    db_position = position_service.get_position_by_id(db, position_id=position_id)
    if not db_position:
        raise HTTPException(status_code=404, detail="Position not found")
    return position_service.update_position(db=db, db_position=db_position, position_update=position_update)


@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_position(position_id: str, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    db_position = position_service.get_position_by_id(db, position_id=position_id)
    if not db_position:
        raise HTTPException(status_code=404, detail="Position not found")
    position_service.delete_position(db=db, db_position=db_position)
    return {"message": "Position deleted"}
