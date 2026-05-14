from datetime import datetime
from config.settings import ABS_WORK_HOURS_START, ABS_WORK_HOURS_END
from services import db_service

# Глобальный override для демо
_abs_override = None

def set_abs_override(value: bool | None):
    global _abs_override
    _abs_override = value

def is_abs_available() -> bool:
    if _abs_override is not None:
        return _abs_override
    hour = datetime.now().hour
    return ABS_WORK_HOURS_START <= hour < ABS_WORK_HOURS_END

def get_abs_status() -> dict:
    available = is_abs_available()
    return {
        "abs_available": available,
        "mode": "override" if _abs_override is not None else "auto",
        "current_hour": datetime.now().hour
    }

def process_payment(payment_id: str, user_id: str, credit_id: str, amount: float) -> dict:
    now = datetime.now().isoformat()
    abs_up = is_abs_available()

    payment = {
        "id": payment_id,
        "user_id": user_id,
        "credit_id": credit_id,
        "amount": amount,
        "status": "completed" if abs_up else "pending",
        "mode": "direct" if abs_up else "middleware",
        "created_at": now,
        "synced_at": now if abs_up else None
    }

    # Сохраняем платёж
    db_service.save_payment(payment)

    # Если АБС недоступна — кладём в очередь
    if not abs_up:
        db_service.add_to_queue(payment)

    # Списываем баланс в любом случае
    db_service.update_user(user_id, {"balance": _new_balance(user_id, amount)})

    return payment

def _new_balance(user_id: str, amount: float) -> float:
    user = db_service.get_user(user_id)
    if user:
        return max(0, user['balance'] - amount)
    return 0

def sync_pending() -> int:
    """Синхронизирует pending платежи с АБС. Вызывается вручную или по крону."""
    if not is_abs_available():
        return 0

    queue = db_service.get_pending_queue()
    now = datetime.now().isoformat()
    count = 0

    for payment in queue:
        payment['status'] = 'completed'
        payment['synced_at'] = now
        db_service.save_payment(payment)
        db_service.remove_from_queue(payment['id'])
        count += 1

    return count
