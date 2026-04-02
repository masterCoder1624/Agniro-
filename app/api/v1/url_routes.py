# app/api/v1/url_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db_dep, get_current_user
from app.services.url_service import create_url, list_urls
from app.schemas.url_schema import UrlCreate, UrlResponse
from typing import List

router = APIRouter()

@router.post("/", response_model=UrlResponse)
def create(payload: UrlCreate, db: Session = Depends(get_db_dep)):
    return create_url(db, payload)

@router.get("/", response_model=List[UrlResponse])
def get_all(db: Session = Depends(get_db_dep), user = Depends(get_current_user)):
    return list_urls(db, user.id)
