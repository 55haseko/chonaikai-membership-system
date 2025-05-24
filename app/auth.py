# app/auth.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.sheets import get_worksheet

router = APIRouter()

# 🔸 入力モデル（会員名と会員番号）
class VerifyRequest(BaseModel):
    name: str
    address: str

# 🔸 認証API（POST /api/verify）
@router.post("/verify")
def verify_member(data: VerifyRequest):
    worksheet = get_worksheet()
    records = worksheet.get_all_records()

    # 🔴 変更ポイント：列名を新しいものに合わせる
    for record in records:
        if (
            record.get("会員名") == data.name and
            record.get("会員番号（丁目、番地、号）") == data.address
        ):
            return {"status": "success", "member": record}

    raise HTTPException(status_code=404, detail="会員情報が見つかりませんでした")
