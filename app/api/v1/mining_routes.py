# app/api/v1/mining_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db_dep, get_current_user
from pydantic import BaseModel
from app.core.llm_client import call_openmining_chat

router = APIRouter()

class ChatReq(BaseModel):
    message: str
    context: dict | None = None

@router.post("/chat")
def chat(req: ChatReq, db: Session = Depends(get_db_dep), user = Depends(get_current_user)):
    # Build simple system prompt using user's profile summary possibility
    system_prompt = "You are JobAdvisorGPT — provide concise, actionable guidance."
    user_prompt = f"User ({user.email}) asked: {req.message}\nContext: {req.context or {}}"
    resp = call_openmining_chat(system_prompt, user_prompt, max_tokens=300)
    return {"answer": resp.get("content"), "meta": resp.get("raw", {})}
