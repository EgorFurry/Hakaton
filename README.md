# IncluBank — HackFusion 2026

Банковское приложение с поддержкой инклюзивности и middleware 24/7.

## Структура проекта

```
inclubank/
├── backend/
│   ├── main.py          ← FastAPI (Никита + ты)
│   └── requirements.txt
├── frontend/
│   ├── index.html       ← PWA (Бекболат)
│   └── manifest.json
└── docs/
    └── API_ДЛЯ_БЕКБОЛАТА.md
```

## Запуск бекенда

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Документация API: http://localhost:8000/docs

## Запуск фронтенда

Просто открыть frontend/index.html в браузере.
Или через Live Server в VS Code (рекомендуется для PWA).

## Сценарий демо для жюри

### 1. Показываем проблему (Direct Legacy Mode)
```
POST /admin/abs { "available": false }
```
→ В приложении видно баннер "Внебанковское время"
→ Платёж всё равно ПРИНИМАЕТСЯ (middleware работает)

### 2. Показываем очередь
```
GET /admin/pending
```
→ Видно что платёж ждёт синхронизации

### 3. Открываем АБС и синхронизируем
```
POST /admin/abs { "available": true }
POST /admin/sync
```
→ Статус платежа меняется на completed ✅

### 4. Показываем инклюзивность
→ Settings → включаем высокий контраст
→ Settings → включаем крупный шрифт
→ На экране оплаты → нажимаем 🎤 → говорим сумму
