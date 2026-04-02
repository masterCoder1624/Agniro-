# app/schemas/job_schema.py
from pydantic import BaseModel
from typing import List, Optional

class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    avg_salary: Optional[str] = None
    demand_score: Optional[float] = 0.0
    required_skills: Optional[List[str]] = []
    mapped_courses: Optional[List[dict]] = []

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: str
    slug: Optional[str]

    class Config:
        orm_mode = True
