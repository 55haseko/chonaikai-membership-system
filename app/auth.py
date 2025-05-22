# app/auth.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.sheets import get_worksheet

router = APIRouter()

# 🔸 入力モデル（氏名と住所）
class VerifyRequest(BaseModel):
    name: str
    address: str

# 🔸 認証API（POST /api/verify）
@router.post("/verify")
def verify_member(data: VerifyRequest):
    worksheet = get_worksheet()
    records = worksheet.get_all_records()

    for record in records:
        if record.get("氏名") == data.name and record.get("住所") == data.address:
            return {"status": "success", "member": record}

    raise HTTPException(status_code=404, detail="会員情報が見つかりませんでした")
