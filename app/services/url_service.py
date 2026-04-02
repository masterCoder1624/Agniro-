# app/services/url_service.py
from sqlalchemy.orm import Session
from app.models.url import Url
from app.schemas.url_schema import UrlCreate

def create_url(db: Session, payload: UrlCreate):
    n = Url(user_id=payload.user_id, title=payload.title, message=payload.message)
    db.add(n)
    db.commit()
    db.refresh(n)
    return n

def list_urls(db: Session, user_id: str, unread_only: bool = False):
    q = db.query(Url).filter(Url.user_id == user_id)
    if unread_only:
        q = q.filter(Url.is_read == False)
    return q.order_by(Url.created_at.desc()).all()
