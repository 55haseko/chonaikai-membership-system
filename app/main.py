from fastapi import FastAPI
from dotenv import load_dotenv
from app import auth, card

load_dotenv()

app = FastAPI()

app.include_router(auth.router, prefix="/api")
app.include_router(card.router, prefix="/api")
