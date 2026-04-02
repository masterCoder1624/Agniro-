# app/services/filter_service.py
from sqlalchemy.orm import Session
from app.models.filter import Filter
from app.schemas.filter_schema import FilterBase
from fastapi import HTTPException

def create_filter(db: Session, payload: FilterBase):
    m = Filter(**payload.dict())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m

def list_filters(db: Session, q: str = None):
    query = db.query(Filter)
    if q:
        query = query.filter(Filter.name.ilike(f"%{q}%"))
    return query.all()

def get_filter(db: Session, filter_id: str):
    m = db.query(Filter).filter(Filter.id == filter_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Filter not found")
    return m

def book_filter(db: Session, filter_id: str, user_id: str, start_time: str, end_time: str):
    # Minimal booking logic: record url for now
    # Real implementation would create a booking table and integrate calendar
    filter = get_filter(db, filter_id)
    # simple check: return success for demo
    return {"filter_id": filter_id, "user_id": user_id, "start_time": start_time, "end_time": end_time, "status": "booked"}
