from datetime import datetime
from config.settings import ABS_WORK_HOURS_START, ABS_WORK_HOURS_END
from services import db_service

_abs_override = None

def check_abs_status() -> dict:
    """
    Отдельный сервис проверки доступности АБИС.
    MW всегда спрашивает сюда перед любой операцией.
    """
    if _abs_override is not None:
        available = _abs_override
    else:
        hour = datetime.now().hour
        available = ABS_WORK_HOURS_START <= hour < ABS_WORK_HOURS_END

    return {
        "available": available,
        "timestamp": datetime.now().isoformat(),
        "mode": "override" if _abs_override is not None else "auto"
    }

def is_abs_available() -> bool:
    return check_abs_status()["available"]

def set_abs_override(value):
    global _abs_override
    _abs_override = value

def get_abs_status() -> dict:
    status = check_abs_status()
    return {
        "abs_available": status["available"],
        "mode": status["mode"],
        "current_hour": datetime.now().hour
    }

def init_cache_from_abis():
    """
    При старте MW копирует данные из АБИС в Cache BD.
    Если АБИС недоступен — работаем с тем что есть в cache.
    """
    if not is_abs_available():
        return {"status": "skipped", "reason": "АБИС недоступен при старте"}

    user = db_service.get_user("user_001")
    if not user:
        db_service.update_user("user_001", {
            "id": "user_001",
            "name": "Алибек Сейткали",
            "balance": 450000.0,
            "accessibility_mode": "normal"
        })

    return {"status": "ok", "message": "Cache BD синхронизирована с АБИС"}

def process_payment(payment_id: str, user_id: str, credit_id: str, amount: float) -> dict:
    """
    Flow по схеме Никиты:
    1. MW получает запрос от клиента
    2. MW вызывает check_abs_status()
    3. АБИС ON  → запрос в АБИС → АБИС пишет в BD → синхронизируем Cache BD
    4. АБИС OFF → пишем в Queue → отвечаем клиенту из Cache BD
    """
    now = datetime.now().isoformat()
    abs_status = check_abs_status()  # шаг 2 — всегда проверяем статус

    if abs_status["available"]:
        status = "completed"
        mode = "direct"
        synced_at = now
    else:
        status = "pending"
        mode = "middleware"
        synced_at = None

    payment = {
        "id": payment_id,
        "user_id": user_id,
        "credit_id": credit_id,
        "amount": amount,
        "status": status,
        "mode": mode,
        "created_at": now,
        "synced_at": synced_at
    }

    db_service.save_payment(payment)

    if not abs_status["available"]:
        db_service.add_to_queue(payment)

    # Синхронизируем Cache BD после каждой операции
    _update_cache(user_id, amount)

    return payment

def _update_cache(user_id: str, amount: float):
    """Обновляем баланс в Cache BD после каждой операции"""
    user = db_service.get_user(user_id)
    if user:
        db_service.update_user(user_id, {"balance": max(0, user['balance'] - amount)})

def sync_pending() -> int:
    """
    Когда АБИС выходит онлайн:
    Queue → MW → АБИС → АБИС обновляет BD
    """
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
