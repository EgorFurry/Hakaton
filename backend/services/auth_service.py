import hashlib, uuid, json, os
from datetime import datetime
from config.settings import DATA_DIR

USERS_FILE   = os.path.join(DATA_DIR, 'users.json')
SESSION_FILE = os.path.join(DATA_DIR, 'sessions.json')

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def _load(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def register(name: str, phone: str, password: str) -> dict:
    users = _load(USERS_FILE)

    # Проверяем что номер не занят
    for u in users.values():
        if u.get("phone") == phone:
            return {"success": False, "message": "Номер уже зарегистрирован"}

    user_id = f"user_{uuid.uuid4().hex[:8]}"
    user = {
        "id": user_id,
        "name": name,
        "phone": phone,
        "password_hash": _hash(password),
        "balance": 450000.0,
        "accessibility_mode": "normal",
        "created_at": datetime.now().isoformat()
    }
    users[user_id] = user
    _save(USERS_FILE, users)

    # Сразу выдаём токен
    token = _create_session(user_id)

    return {
        "success": True,
        "token": token,
        "user_id": user_id,
        "name": name,
        "message": "Регистрация успешна"
    }

def login(phone: str, password: str) -> dict:
    users = _load(USERS_FILE)

    for user in users.values():
        if user.get("phone") == phone and user.get("password_hash") == _hash(password):
            token = _create_session(user["id"])
            return {
                "success": True,
                "token": token,
                "user_id": user["id"],
                "name": user["name"],
                "message": "Вход выполнен"
            }

    return {"success": False, "message": "Неверный номер или пароль"}

def _create_session(user_id: str) -> str:
    sessions = _load(SESSION_FILE)
    token = uuid.uuid4().hex
    sessions[token] = {
        "user_id": user_id,
        "created_at": datetime.now().isoformat()
    }
    _save(SESSION_FILE, sessions)
    return token

def get_by_token(token: str) -> dict | None:
    sessions = _load(SESSION_FILE)
    session = sessions.get(token)
    if not session:
        return None

    users = _load(USERS_FILE)
    user = users.get(session["user_id"])
    if not user:
        return None

    # Не возвращаем хэш пароля
    return {k: v for k, v in user.items() if k != "password_hash"}
