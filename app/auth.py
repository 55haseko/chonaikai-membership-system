# app/auth.py

from fastapi import APIRouter, HTTPException
from app.sheets import find_member_by_line_id

router = APIRouter()

@router.get("/auth/{line_user_id}")
def auth(line_user_id: str):
    member = find_member_by_line_id(line_user_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member
