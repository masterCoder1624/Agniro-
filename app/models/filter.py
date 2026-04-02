# app/models/filter.py
import uuid
from sqlalchemy import Column, String, Text, Float
from sqlalchemy import JSON
from app.database import Base

class Filter(Base):
    __tablename__ = "filters"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    bio = Column(Text, nullable=True)
    expertise = Column(JSON, default=[])
    rating = Column(Float, default=0.0)
    availability = Column(JSON, default=[])  # simple list of available slots
    contact = Column(String, nullable=True)
