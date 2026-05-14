from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import payment, admin, accessibility, user

app = FastAPI(title="IncluBank API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(user.router)
app.include_router(payment.router)
app.include_router(admin.router)
app.include_router(accessibility.router)

@app.get("/")
def root():
    return {"project": "IncluBank", "version": "2.0", "docs": "/docs"}
