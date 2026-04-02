# app/schemas/url_schema.py
from pydantic import BaseModel

class UrlCreate(BaseModel):
    user_id: str
    title: str
    message: str

class UrlResponse(UrlCreate):
    id: str
    is_read: bool
    created_at: str

    class Config:
        orm_mode = True
