from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    name: str
    phone: str      # номер телефона как логин (как в Kaspi)
    password: str

class LoginRequest(BaseModel):
    phone: str
    password: str

@router.post("/register")
def register(req: RegisterRequest):
    """Регистрация нового пользователя"""
    result = auth_service.register(req.name, req.phone, req.password)
    if not result["success"]:
        raise HTTPException(400, result["message"])
    return result

@router.post("/login")
def login(req: LoginRequest):
    """Вход по номеру телефона и паролю"""
    result = auth_service.login(req.phone, req.password)
    if not result["success"]:
        raise HTTPException(401, result["message"])
    return result

@router.get("/me/{token}")
def get_me(token: str):
    """Получить данные по токену"""
    user = auth_service.get_by_token(token)
    if not user:
        raise HTTPException(401, "Токен недействителен")
    return user
