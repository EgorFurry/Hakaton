from fastapi import APIRouter, HTTPException
from services import db_service

router = APIRouter(prefix="/api", tags=["users"])

@router.get("/user/{user_id}")
def get_user(user_id: str):
    user = db_service.get_user(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return user
