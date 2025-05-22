# app/main.py

from fastapi import FastAPI
from app import auth
from dotenv import load_dotenv
from app import auth, card

load_dotenv()

app = FastAPI()  # ← ここが必要！

app.include_router(auth.router, prefix="/api")
app.include_router(card.router, prefix="/api")