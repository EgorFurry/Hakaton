from fastapi import APIRouter
from pydantic import BaseModel
from services import abs_service, db_service

router = APIRouter(prefix="/admin", tags=["admin"])

class AbsOverride(BaseModel):
    available: bool

@router.get("/abs-status")
def abs_status():
    return abs_service.get_abs_status()

@router.post("/abs")
def set_abs(req: AbsOverride):
    """Переключить АБС для демо"""
    abs_service.set_abs_override(req.available)
    return {"abs_available": req.available}

@router.post("/abs/auto")
def set_abs_auto():
    """Вернуть АБС в автоматический режим (по времени)"""
    abs_service.set_abs_override(None)
    return {"mode": "auto"}

@router.post("/sync")
def sync():
    """Синхронизировать pending платежи с АБС"""
    count = abs_service.sync_pending()
    return {"synced": count, "message": f"Синхронизировано: {count}"}

@router.get("/pending")
def pending():
    """Список платежей в очереди"""
    return db_service.get_pending_queue()
