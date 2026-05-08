from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any

# Assuming these exist in your project structure
try:
    from app.database import get_db
    from app.models.job import Job
except ImportError:
    # Fallback to prevent immediate crash if not defined yet
    def get_db(): yield None
    class Job: pass

router = APIRouter(prefix="/api/v1/queue")

class JobCreate(BaseModel):
    task_name: str
    payload: Dict[str, Any] = {}

@router.post("/jobs")
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    db_job = Job(task_name=job_in.task_name, payload=job_in.payload, status="PENDING")
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return {"job_id": db_job.id, "status": db_job.status}

@router.get("/jobs/{job_id}")
def get_job_status(job_id: int, db: Session = Depends(get_db)):
    db_job = db.query(Job).filter(Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": db_job.id, "task_name": db_job.task_name, "status": db_job.status}
