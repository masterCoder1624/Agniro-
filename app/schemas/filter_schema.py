# app/schemas/filter_schema.py
from pydantic import BaseModel
from typing import List, Optional

class FilterBase(BaseModel):
    name: str
    bio: Optional[str] = None
    expertise: Optional[List[str]] = []
    rating: Optional[float] = 0.0
    availability: Optional[List[dict]] = []
    contact: Optional[str] = None

class FilterResponse(FilterBase):
    id: str

    class Config:
        orm_mode = True

class FilterBookingRequest(BaseModel):
    filter_id: str
    user_id: str
    start_time: str  # ISO timestamps expected
    end_time: str
