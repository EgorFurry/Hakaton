from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import abs_service, db_service
import uuid

router = APIRouter(prefix="/api", tags=["payments"])

class PaymentCreate(BaseModel):
    user_id: str
    credit_id: str
    amount: float

@router.get("/credit/status/{user_id}")
def credit_status(user_id: str):
    """Статус кредита пользователя"""
    user = db_service.get_user(user_id)
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    return {
        "user_id": user_id,
        "credit_id": "credit_001",
        "total_debt": 1200000,
        "monthly_payment": 85000,
        "balance": user['balance']
    }

@router.post("/payment/create")
def payment_create(req: PaymentCreate):
    """
    Создать платёж.
    Клиент всегда видит успех — middleware скрывает статус АБС.
    """
    payment_id = str(uuid.uuid4())
    payment = abs_service.process_payment(
        payment_id, req.user_id, req.credit_id, req.amount
    )
    return {
        "payment_id": payment['id'],
        "status": "success",           # клиент всегда видит success
        "internal_status": payment['status'],
        "mode": payment['mode'],
        "amount": req.amount,
        "message": "Платёж успешно принят"
    }

@router.get("/payment/process/{payment_id}")
def payment_process(payment_id: str):
    """Статус обработки платежа"""
    payment = db_service.get_payment(payment_id)
    if not payment:
        raise HTTPException(404, "Платёж не найден")
    return payment

@router.get("/payment/history/{user_id}")
def payment_history(user_id: str):
    """История платежей пользователя"""
    return db_service.get_user_payments(user_id)
