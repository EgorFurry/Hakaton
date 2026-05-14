import json, os
from config.settings import PAYMENTS_FILE, USERS_FILE, QUEUE_FILE, ACCESS_FILE

# ─── Дефолтные данные ───
DEFAULT_USERS = {
    "user_001": {
        "id": "user_001",
        "name": "Алибек Сейткали",
        "balance": 450000.0,
        "accessibility_mode": "normal"
    }
}

DEFAULT_PAYMENTS    = {}
DEFAULT_QUEUE       = {}
DEFAULT_ACCESSIBILITY = {}

def _load(path, default):
    if not os.path.exists(path):
        _save(path, default)
        return default
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── Users ───
def get_user(user_id: str):
    users = _load(USERS_FILE, DEFAULT_USERS)
    return users.get(user_id)

def update_user(user_id: str, fields: dict):
    users = _load(USERS_FILE, DEFAULT_USERS)
    if user_id in users:
        users[user_id].update(fields)
        _save(USERS_FILE, users)
    return users.get(user_id)

# ─── Payments ───
def save_payment(payment: dict):
    payments = _load(PAYMENTS_FILE, DEFAULT_PAYMENTS)
    payments[payment['id']] = payment
    _save(PAYMENTS_FILE, payments)

def get_payment(payment_id: str):
    payments = _load(PAYMENTS_FILE, DEFAULT_PAYMENTS)
    return payments.get(payment_id)

def get_user_payments(user_id: str):
    payments = _load(PAYMENTS_FILE, DEFAULT_PAYMENTS)
    result = [p for p in payments.values() if p['user_id'] == user_id]
    return sorted(result, key=lambda x: x['created_at'], reverse=True)[:10]

# ─── Queue ───
def add_to_queue(payment: dict):
    queue = _load(QUEUE_FILE, DEFAULT_QUEUE)
    queue[payment['id']] = payment
    _save(QUEUE_FILE, queue)

def get_pending_queue():
    return list(_load(QUEUE_FILE, DEFAULT_QUEUE).values())

def remove_from_queue(payment_id: str):
    queue = _load(QUEUE_FILE, DEFAULT_QUEUE)
    queue.pop(payment_id, None)
    _save(QUEUE_FILE, queue)

# ─── Accessibility ───
def get_accessibility(user_id: str):
    data = _load(ACCESS_FILE, DEFAULT_ACCESSIBILITY)
    return data.get(user_id, {"mode": "normal"})

def save_accessibility(user_id: str, mode: str):
    data = _load(ACCESS_FILE, DEFAULT_ACCESSIBILITY)
    data[user_id] = {"mode": mode}
    _save(ACCESS_FILE, data)
