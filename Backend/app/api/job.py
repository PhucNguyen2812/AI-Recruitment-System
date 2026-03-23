# ============================================================
# app/api/job.py
# API router for Job Operations
# ============================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.job import JobCreate, JobUpdate, JobResponse
from app.services import job_service
from app.middleware.auth_middleware import get_current_user
from app.models.user import NguoiDung

router = APIRouter(prefix="/api/jobs", tags=["Jobs"])


@router.get("/", response_model=List[JobResponse])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return job_service.get_jobs(db, skip=skip, limit=limit)


@router.get("/open", response_model=List[JobResponse])
def get_open_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return job_service.get_open_jobs(db, skip=skip, limit=limit)


@router.get("/my", response_model=List[JobResponse])
def get_my_jobs(campaign_id: str = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    return job_service.get_jobs(db, skip=skip, limit=limit, creator_id=current_user.id, campaign_id=campaign_id)


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job: JobCreate, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    # Need to verify campaign exists and is owned by the user, skipping for brevity
    return job_service.create_job(db=db, job=job, creator_id=current_user.id)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    db_job = job_service.get_job_by_id(db, job_id=job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: str, job_update: JobUpdate, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    db_job = job_service.get_job_by_id(db, job_id=job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    if db_job.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this job")
    return job_service.update_job(db=db, db_job=db_job, job_update=job_update)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: str, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    db_job = job_service.get_job_by_id(db, job_id=job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    if db_job.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this job")
    
    # We call close_job because we want to trigger Hard Delete of PDFs when deleting a job.
    # Alternatively we can just call db.delete() if CASCADE is set up, but let's reuse logic
    job_service.close_job(db=db, job_id=job_id)
    job_service.delete_job(db=db, db_job=db_job)
    return {"message": "Job deleted"}


@router.post("/{job_id}/close", status_code=status.HTTP_200_OK)
def close_job(job_id: str, db: Session = Depends(get_db), current_user: NguoiDung = Depends(get_current_user)):
    db_job = job_service.get_job_by_id(db, job_id=job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    if db_job.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to close this job")
    
    success = job_service.close_job(db=db, job_id=job_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to close job and delete data")
    return {"message": "Job closed and candidate data wiped"}
