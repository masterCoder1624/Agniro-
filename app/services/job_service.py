# app/services/job_service.py
from sqlalchemy.orm import Session
from app.models.job import Job
from app.schemas.job_schema import JobCreate
from fastapi import HTTPException
from typing import List

def create_job(db: Session, payload: JobCreate):
    c = Job(**payload.dict())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c

def list_jobs(db: Session, q: str = None, limit: int = 50):
    query = db.query(Job)
    if q:
        query = query.filter(Job.title.ilike(f"%{q}%"))
    return query.limit(limit).all()

def get_job(db: Session, job_id: str):
    c = db.query(Job).filter(Job.id == job_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Job not found")
    return c

def recommend_jobs_from_skills(db: Session, skills: List[str], top_k: int = 5):
    # Simple scoring: count overlap of skills
    jobs = db.query(Job).all()
    scored = []
    sset = set([s.lower().strip() for s in skills])
    for c in jobs:
        req = set([x.lower().strip() for x in (c.required_skills or [])])
        match_count = len(sset & req)
        score = match_count / (len(req) + 1)
        scored.append((score, c))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for sc, c in scored[:top_k]]
