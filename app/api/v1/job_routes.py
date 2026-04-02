# app/api/v1/job_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db_dep, get_current_user
from app.schemas.job_schema import JobCreate, JobResponse
from app.services.job_service import create_job, list_jobs, get_job, recommend_jobs_from_skills
from app.core.recommender import generate_basic_roadmap

router = APIRouter()

@router.post("/", response_model=JobResponse)
def create(payload: JobCreate, db: Session = Depends(get_db_dep)):
    return create_job(db, payload)

@router.get("/", response_model=List[JobResponse])
def get_all(q: str = None, db: Session = Depends(get_db_dep)):
    return list_jobs(db, q=q)

@router.get("/{job_id}", response_model=JobResponse)
def detail(job_id: str, db: Session = Depends(get_db_dep)):
    return get_job(db, job_id)

@router.post("/analyze")
def analyze(skills: List[str], db: Session = Depends(get_db_dep)):
    recs = recommend_jobs_from_skills(db, skills)
    return {"recommended_jobs": [JobResponse.from_orm(c) for c in recs]}

@router.get("/{job_id}/roadmap")
def roadmap(job_id: str, db: Session = Depends(get_db_dep)):
    c = get_job(db, job_id)
    return generate_basic_roadmap(c.title)
