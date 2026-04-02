# app/models/job.py
import uuid
from sqlalchemy import Column, String, Text, Float
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from app.database import Base
from sqlalchemy import JSON

# Using simple UUID stored as text for SQLite compatibility
class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, index=True)
    slug = Column(String, nullable=True, index=True)
    description = Column(Text, nullable=True)
    avg_salary = Column(String, nullable=True)
    demand_score = Column(Float, default=0.0)
    required_skills = Column(JSON, default=[])
    mapped_courses = Column(JSON, default=[])
