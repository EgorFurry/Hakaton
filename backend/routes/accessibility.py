from fastapi import APIRouter
from pydantic import BaseModel
from services import db_service, ai_service

router = APIRouter(prefix="/api/accessibility", tags=["accessibility"])

class AccessibilityUpdate(BaseModel):
    user_id: str
    mode: str  # normal | high_contrast | large_font | blind

class AiQuestion(BaseModel):
    question: str
    user_id: str = "user_001"

@router.get("/{user_id}")
def get_settings(user_id: str):
    return db_service.get_accessibility(user_id)

@router.post("/settings")
def update_settings(req: AccessibilityUpdate):
    allowed = {"normal", "high_contrast", "large_font", "blind"}
    if req.mode not in allowed:
        return {"error": f"Режим должен быть одним из: {allowed}"}
    db_service.save_accessibility(req.user_id, req.mode)
    # Обновляем и в users.json тоже
    db_service.update_user(req.user_id, {"accessibility_mode": req.mode})
    return {"status": "ok", "mode": req.mode}

@router.post("/ai/ask")
async def ai_ask(req: AiQuestion):
    """AI-ассистент отвечает на вопросы пользователя"""
    answer = await ai_service.ask_ai(req.question)
    return {"answer": answer}
