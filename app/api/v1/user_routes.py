# app/api/v1/user_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db_dep, get_current_user
from app.schemas.user_schema import UserResponse
from app.services.user_service import get_user_by_email

router = APIRouter()

@router.get("/me", response_model=UserResponse)
def me(user = Depends(get_current_user)):
    return user
