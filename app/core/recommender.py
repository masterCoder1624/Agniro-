# app/core/recommender.py
from typing import List
from sqlalchemy.orm import Session
from app.services.job_service import recommend_jobs_from_skills

def skills_to_jobs(db: Session, skills: List[str], top_k: int = 5):
    return recommend_jobs_from_skills(db, skills, top_k=top_k)

def generate_basic_roadmap(job_title: str):
    # Simple rule-based roadmap generator; replace with LLM calls to enhance.
    common_steps = [
        "Understand fundamentals",
        "Complete relevant online courses",
        "Build 2-3 projects",
        "Publish portfolio",
        "Apply for internships",
        "Prepare for interviews"
    ]
    return {"job": job_title, "steps": common_steps}
