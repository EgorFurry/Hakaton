from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import sqlite3, uuid, os

app = FastAPI(title="IncluBank API")

# CORS — чтобы PWA мог обращаться к API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "inclubank.db"

# ───────────────────────────────────────────
# БД — инициализация
# ───────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            credit_id TEXT,
            amount REAL,
            status TEXT,       -- pending | completed | failed
            created_at TEXT,
            synced_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            balance REAL,
            accessibility_mode TEXT  -- normal | high_contrast | large_font
        )
    """)
    # Тестовый юзер
    c.execute("""
        INSERT OR IGNORE INTO users VALUES
        ('user_001', 'Алибек Сейткали', 450000.0, 'normal')
    """)
    conn.commit()
    conn.close()

init_db()

# ───────────────────────────────────────────
# Хелперы
# ───────────────────────────────────────────
def get_db():
    return sqlite3.connect(DB_PATH)

def is_abs_available() -> bool:
    """
    Имитируем легаси АБС: работает только 9:00–18:00.
    Можно переключить вручную через /admin/abs для демо на хакатоне.
    """
    hour = datetime.now().hour
    return 9 <= hour < 18

# Глобальный флаг для ручного переключения на демо
abs_override = None  # None = по времени, True/False = принудительно

# ───────────────────────────────────────────
# Модели запросов
# ───────────────────────────────────────────
class PaymentRequest(BaseModel):
    user_id: str
    credit_id: str
    amount: float

class AccessibilityUpdate(BaseModel):
    user_id: str
    mode: str  # normal | high_contrast | large_font

class AbsOverride(BaseModel):
    available: bool  # для демо: вручную закрыть/открыть АБС

# ───────────────────────────────────────────
# ЭНДПОИНТЫ
# ───────────────────────────────────────────

@app.get("/")
def root():
    return {"project": "IncluBank", "status": "running"}


@app.get("/user/{user_id}")
def get_user(user_id: str):
    """Данные юзера — фронт показывает на главном экране"""
    conn = get_db()
    row = conn.execute(
        "SELECT id, name, balance, accessibility_mode FROM users WHERE id=?",
        (user_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Пользователь не найден")
    return {
        "id": row[0],
        "name": row[1],
        "balance": row[2],
        "accessibility_mode": row[3]
    }


@app.post("/payment")
def create_payment(req: PaymentRequest):
    """
    Главный эндпоинт — погашение кредита.
    Два режима:
      - АБС доступна → completed сразу
      - АБС недоступна → pending, синхронизация позже
    Клиент в обоих случаях видит успех.
    """
    global abs_override
    abs_up = abs_override if abs_override is not None else is_abs_available()

    payment_id = str(uuid.uuid4())
    now = datetime.now().isoformat()

    if abs_up:
        status = "completed"
        synced_at = now
        mode_label = "direct"
    else:
        status = "pending"
        synced_at = None
        mode_label = "middleware"

    conn = get_db()
    conn.execute(
        "INSERT INTO payments VALUES (?,?,?,?,?,?,?)",
        (payment_id, req.user_id, req.credit_id, req.amount, status, now, synced_at)
    )
    # Списываем с баланса в любом случае
    conn.execute(
        "UPDATE users SET balance = balance - ? WHERE id=?",
        (req.amount, req.user_id)
    )
    conn.commit()
    conn.close()

    return {
        "payment_id": payment_id,
        "status": "success",        # фронт ВСЕГДА видит success
        "internal_status": status,  # для admin-панели
        "mode": mode_label,
        "amount": req.amount,
        "message": "Платёж успешно проведён"
    }


@app.get("/payment/{payment_id}")
def get_payment_status(payment_id: str):
    """Статус конкретного платежа"""
    conn = get_db()
    row = conn.execute(
        "SELECT id, amount, status, created_at, synced_at FROM payments WHERE id=?",
        (payment_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Платёж не найден")
    return {
        "payment_id": row[0],
        "amount": row[1],
        "status": row[2],
        "created_at": row[3],
        "synced_at": row[4]
    }


@app.get("/payments/{user_id}")
def get_user_payments(user_id: str):
    """История платежей юзера — для экрана транзакций"""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, credit_id, amount, status, created_at FROM payments WHERE user_id=? ORDER BY created_at DESC LIMIT 10",
        (user_id,)
    ).fetchall()
    conn.close()
    return [
        {"payment_id": r[0], "credit_id": r[1], "amount": r[2], "status": r[3], "created_at": r[4]}
        for r in rows
    ]


@app.post("/accessibility")
def update_accessibility(req: AccessibilityUpdate):
    """Сохраняем режим доступности юзера"""
    allowed = {"normal", "high_contrast", "large_font"}
    if req.mode not in allowed:
        raise HTTPException(400, f"Режим должен быть одним из: {allowed}")
    conn = get_db()
    conn.execute(
        "UPDATE users SET accessibility_mode=? WHERE id=?",
        (req.mode, req.user_id)
    )
    conn.commit()
    conn.close()
    return {"status": "ok", "mode": req.mode}


# ───────────────────────────────────────────
# ADMIN — для демо на хакатоне
# ───────────────────────────────────────────

@app.get("/admin/abs-status")
def abs_status():
    """Показывает текущий статус АБС — для демо-панели"""
    global abs_override
    actual = abs_override if abs_override is not None else is_abs_available()
    return {
        "abs_available": actual,
        "mode": "override" if abs_override is not None else "auto",
        "current_hour": datetime.now().hour
    }


@app.post("/admin/abs")
def set_abs(req: AbsOverride):
    """
    Вручную включить/выключить АБС для демо.
    На защите: сначала показываем выключенную АБС (middleware),
    потом включаем и показываем синхронизацию.
    """
    global abs_override
    abs_override = req.available
    return {"abs_available": abs_override}


@app.post("/admin/sync")
def manual_sync():
    """
    Синхронизация pending платежей с АБС.
    Вызывается вручную или по крону.
    """
    global abs_override
    abs_up = abs_override if abs_override is not None else is_abs_available()
    if not abs_up:
        return {"synced": 0, "message": "АБС недоступна, синхронизация отложена"}

    conn = get_db()
    now = datetime.now().isoformat()
    cursor = conn.execute(
        "UPDATE payments SET status='completed', synced_at=? WHERE status='pending'",
    )
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return {"synced": count, "message": f"Синхронизировано платежей: {count}"}


@app.get("/admin/pending")
def get_pending():
    """Список ожидающих синхронизации платежей"""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, user_id, amount, created_at FROM payments WHERE status='pending'"
    ).fetchall()
    conn.close()
    return [{"id": r[0], "user_id": r[1], "amount": r[2], "created_at": r[3]} for r in rows]
