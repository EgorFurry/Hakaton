import os

# АБС настройки
ABS_WORK_HOURS_START = 9
ABS_WORK_HOURS_END = 18

# Пути к JSON хранилищу
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
PAYMENTS_FILE = os.path.join(DATA_DIR, 'payments.json')
USERS_FILE    = os.path.join(DATA_DIR, 'users.json')
QUEUE_FILE    = os.path.join(DATA_DIR, 'queue.json')
ACCESS_FILE   = os.path.join(DATA_DIR, 'accessibility.json')

# Gemini API (берётся из .env)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
