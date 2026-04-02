# app/api/v1/filter_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db_dep, get_current_user
from app.services.filter_service import create_filter, list_filters, get_filter, book_filter
from app.schemas.filter_schema import FilterBase, FilterResponse, FilterBookingRequest

router = APIRouter()

@router.post("/", response_model=FilterResponse)
def create(payload: FilterBase, db: Session = Depends(get_db_dep)):
    return create_filter(db, payload)

@router.get("/", response_model=List[FilterResponse])
def all_filters(q: str = None, db: Session = Depends(get_db_dep)):
    return list_filters(db, q=q)

@router.get("/{filter_id}", response_model=FilterResponse)
def get_one(filter_id: str, db: Session = Depends(get_db_dep)):
    return get_filter(db, filter_id)

@router.post("/book")
def book(payload: FilterBookingRequest, db: Session = Depends(get_db_dep), user = Depends(get_current_user)):
    # user is validated; booking uses provided user_id or current user
    return book_filter(db, payload.filter_id, payload.user_id or user.id, payload.start_time, payload.end_time)
