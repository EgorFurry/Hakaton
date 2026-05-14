# API контракт v2 — IncluBank
# Скидывай Бекболату целиком

BASE_URL = "http://localhost:8000"

## ───────────────────────────────
## 1. Данные пользователя
## Экран: Dashboard (имя, баланс)
## ───────────────────────────────

GET /api/user/user_001

Ответ:
{
  "id": "user_001",
  "name": "Алибек Сейткали",
  "balance": 450000.0,
  "accessibility_mode": "normal"
}

JS:
  const res = await fetch(`${BASE_URL}/api/user/user_001`);
  const user = await res.json();


## ───────────────────────────────
## 2. Статус кредита
## Экран: Dashboard (долг, платёж)
## ───────────────────────────────

GET /api/credit/status/user_001

Ответ:
{
  "user_id": "user_001",
  "credit_id": "credit_001",
  "total_debt": 1200000,
  "monthly_payment": 85000,
  "balance": 450000.0
}


## ───────────────────────────────
## 3. Создать платёж
## Экран: Погашение → кнопка "Оплатить"
## ───────────────────────────────

POST /api/payment/create
Content-Type: application/json

Тело:
{
  "user_id": "user_001",
  "credit_id": "credit_001",
  "amount": 50000
}

Ответ (ВСЕГДА успех — middleware скрывает статус АБС):
{
  "payment_id": "uuid-...",
  "status": "success",
  "mode": "middleware",   // или "direct"
  "amount": 50000,
  "message": "Платёж успешно принят"
}

JS:
  const res = await fetch(`${BASE_URL}/api/payment/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 'user_001', credit_id: 'credit_001', amount })
  });
  const data = await res.json();
  if (data.status === 'success') showSuccessScreen(data);

Подсказка UI:
  mode === 'middleware' → показать "⏳ Платёж будет обработан автоматически"
  mode === 'direct'    → показать "✅ Платёж проведён через АБС"


## ───────────────────────────────
## 4. Статус конкретного платежа
## Экран: детали операции
## ───────────────────────────────

GET /api/payment/process/{payment_id}

Ответ:
{
  "id": "uuid-...",
  "user_id": "user_001",
  "amount": 50000,
  "status": "pending",    // pending | completed
  "mode": "middleware",
  "created_at": "2026-05-15T10:00:00",
  "synced_at": null
}


## ───────────────────────────────
## 5. История платежей
## Экран: Transactions
## ───────────────────────────────

GET /api/payment/history/user_001

Ответ:
[
  {
    "id": "uuid-...",
    "amount": 50000,
    "status": "completed",   // completed | pending
    "mode": "direct",
    "created_at": "2026-05-15T10:00:00",
    "synced_at": "2026-05-15T10:00:01"
  }
]

Подсказка UI:
  status === 'pending'   → иконка ⏳, текст "Ожидает синхронизации"
  status === 'completed' → иконка ✅, зелёный цвет


## ───────────────────────────────
## 6. Настройки доступности
## Экран: Settings → AI accessibility panel
## ───────────────────────────────

POST /api/accessibility/settings
Content-Type: application/json

Тело:
{
  "user_id": "user_001",
  "mode": "high_contrast"   // normal | high_contrast | large_font | blind
}

Ответ:
{ "status": "ok", "mode": "high_contrast" }

JS:
  await fetch(`${BASE_URL}/api/accessibility/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 'user_001', mode })
  });


## ───────────────────────────────
## 7. AI-ассистент
## Экран: AI helper panel / кнопка "Спросить"
## ───────────────────────────────

POST /api/accessibility/ai/ask
Content-Type: application/json

Тело:
{
  "user_id": "user_001",
  "question": "Как погасить кредит?"
}

Ответ:
{
  "answer": "Чтобы погасить кредит, перейдите в раздел Погашение, введите сумму и нажмите Оплатить."
}

JS:
  const res = await fetch(`${BASE_URL}/api/accessibility/ai/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 'user_001', question: userInput })
  });
  const { answer } = await res.json();
  // показать answer в AI helper panel


## ───────────────────────────────
## 8. Статус АБС — баннер
## Экран: Dashboard (баннер сверху)
## ───────────────────────────────

GET /admin/abs-status

Ответ:
{
  "abs_available": false,
  "mode": "override",
  "current_hour": 2
}

JS (опрашивать каждые 30 сек):
  const { abs_available } = await (await fetch(`${BASE_URL}/admin/abs-status`)).json();
  if (!abs_available) showBanner("⏳ Внебанковское время. Платежи обработаются утром.");


## ───────────────────────────────
## КАК ЗАПУСТИТЬ БЕК
## ───────────────────────────────

cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

Документация (все эндпоинты): http://localhost:8000/docs


## ───────────────────────────────
## СЦЕНАРИЙ ДЕМО ДЛЯ ЖЮРИ
## ───────────────────────────────

Шаг 1. POST /admin/abs { "available": false }     ← АБС выключена
        → В приложении появляется баннер

Шаг 2. Оплатить кредит в приложении
        → Клиент видит "Успешно" ✅
        → mode === "middleware"

Шаг 3. GET /admin/pending
        → Показать жюри: платёж ждёт в очереди

Шаг 4. POST /admin/abs { "available": true }       ← АБС включена
        POST /admin/sync                            ← синхронизация

Шаг 5. GET /api/payment/history/user_001
        → status === "completed" ✅

Шаг 6. Показать accessibility:
        → Settings → включить "Режим для слабовидящих"
        → Нажать любую кнопку — озвучит текст
        → Нажать второй раз — выполнит действие
        → Показать AI-ассистента: задать вопрос голосом
