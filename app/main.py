# app/main.py

from fastapi import FastAPI
from app import auth
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()  # ← ここが必要！

app.include_router(auth.router, prefix="/api")
