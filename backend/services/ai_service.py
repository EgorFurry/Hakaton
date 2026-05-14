import httpx
from config.settings import GEMINI_API_KEY

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

SYSTEM_PROMPT = """Ты — AI-ассистент банковского приложения IncluBank.
Помогаешь пользователям с операциями и навигацией.
Особенно помогаешь людям с ограниченными возможностями.
Отвечай кратко, по-русски, простым языком."""

async def ask_ai(question: str) -> str:
    if not GEMINI_API_KEY:
        return "AI-ассистент недоступен. Настройте GEMINI_API_KEY в .env файле."

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"{SYSTEM_PROMPT}\n\nВопрос: {question}"}]}
        ]
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                json=payload
            )
            data = res.json()
            return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Ошибка AI: {str(e)}"
