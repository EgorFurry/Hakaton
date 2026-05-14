from fastapi import APIRouter
from pydantic import BaseModel
from services import abs_service, db_service

router = APIRouter(tags=["system"])

class AbsOverride(BaseModel):
    available: bool

# ─── /check/status — по схеме Никиты ───
@router.get("/check/status")
def check_status():
    """
    MW вызывает этот эндпоинт перед каждой операцией.
    Проверяет доступность АБИС прямо сейчас.
    """
    return abs_service.check_abs_status()

@router.get("/check/init-cache")
def init_cache():
    """При старте — синхронизировать Cache BD с АБИС"""
    return abs_service.init_cache_from_abis()

# ─── /admin/* — для демо ───
@router.get("/admin/abs-status")
def abs_status():
    return abs_service.get_abs_status()

@router.post("/admin/abs")
def set_abs(req: AbsOverride):
    """Переключить АБС для демо"""
    abs_service.set_abs_override(req.available)
    return {"abs_available": req.available}

@router.post("/admin/abs/auto")
def set_abs_auto():
    abs_service.set_abs_override(None)
    return {"mode": "auto"}

@router.post("/admin/sync")
def sync():
    """Когда АБИС выходит онлайн — синхронизируем Queue → АБИС"""
    count = abs_service.sync_pending()
    return {"synced": count, "message": f"Синхронизировано: {count}"}

@router.get("/admin/pending")
def pending():
    """Платежи в очереди ожидающие АБИС"""
    return db_service.get_pending_queue()
