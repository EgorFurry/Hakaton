# API контракт — IncluBank
# Скидывай Бекболату целиком

BASE_URL = "http://localhost:8000"

## ───────────────────────────────
## 1. Получить данные пользователя
## Экран: Home (баланс, имя)
## ───────────────────────────────

GET /user/user_001

Ответ:
{
  "id": "user_001",
  "name": "Алибек Сейткали",
  "balance": 450000.0,
  "accessibility_mode": "normal"   // normal | high_contrast | large_font
}

JS пример:
  const res = await fetch(`${BASE_URL}/user/user_001`);
  const user = await res.json();
  document.getElementById('balance').textContent = user.balance + ' ₸';


## ───────────────────────────────
## 2. Погасить кредит
## Экран: Погашение кредита → кнопка "Оплатить"
## ───────────────────────────────

POST /payment
Content-Type: application/json

Тело:
{
  "user_id": "user_001",
  "credit_id": "credit_001",
  "amount": 50000
}

Ответ (ВСЕГДА успех — даже если АБС закрыта):
{
  "payment_id": "uuid-...",
  "status": "success",
  "mode": "middleware",    // или "direct" — для демо, можно показать в UI
  "amount": 50000,
  "message": "Платёж успешно проведён"
}

JS пример:
  const res = await fetch(`${BASE_URL}/payment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 'user_001', credit_id: 'credit_001', amount: amount })
  });
  const data = await res.json();
  if (data.status === 'success') showSuccessScreen(data);


## ───────────────────────────────
## 3. История транзакций
## Экран: Transactions
## ───────────────────────────────

GET /payments/user_001

Ответ:
[
  {
    "payment_id": "uuid-...",
    "credit_id": "credit_001",
    "amount": 50000,
    "status": "completed",   // completed | pending
    "created_at": "2026-05-15T10:23:00"
  }
]

Подсказка: если status === 'pending' — покажи иконку часиков (синхронизируется)
           если status === 'completed' — зелёная галочка


## ───────────────────────────────
## 4. Настройки доступности (AI кейс AKSiT)
## Экран: Settings → accessibility
## ───────────────────────────────

POST /accessibility
Content-Type: application/json

Тело:
{
  "user_id": "user_001",
  "mode": "high_contrast"    // normal | high_contrast | large_font
}

Ответ:
{ "status": "ok", "mode": "high_contrast" }

JS пример (при переключении тоггла):
  async function setAccessibility(mode) {
    await fetch(`${BASE_URL}/accessibility`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'user_001', mode })
    });
    applyTheme(mode);  // сразу применяем локально
  }


## ───────────────────────────────
## 5. Статус АБС — для демо-баннера
## Показывать на главном экране: "АБС доступна / недоступна"
## ───────────────────────────────

GET /admin/abs-status

Ответ:
{
  "abs_available": false,
  "mode": "override",
  "current_hour": 2
}

Подсказка: если abs_available === false → показывай баннер
           "Внебанковское время. Платежи принимаются и будут обработаны утром."


## ───────────────────────────────
## КАК ЗАПУСТИТЬ БЕК
## ───────────────────────────────

cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

Документация API автоматом: http://localhost:8000/docs


## ───────────────────────────────
## СЦЕНАРИЙ ДЕМО ДЛЯ ЖЮРИ
## ───────────────────────────────

Шаг 1. Открыть http://localhost:8000/docs
        POST /admin/abs { "available": false }   ← АБС выключена

Шаг 2. В приложении: оплатить кредит 250 000 ₸
        Клиент видит: "Платёж успешно проведён" ✅
        mode в ответе: "middleware"

Шаг 3. GET /admin/pending → показать жюри что платёж в очереди

Шаг 4. POST /admin/abs { "available": true }     ← АБС включена
        POST /admin/sync                          ← синхронизация

Шаг 5. GET /payments/user_001 → статус "completed" ✅
        Жюри видит: платёж прошёл через middleware и синхронизировался
