from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.sheets import get_worksheet
import re

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# 🔹 表記揺れ補正関数
def normalize(text: str) -> str:
    if not text:
        return ""
    # 空白除去
    text = text.replace(" ", "").replace("　", "")
    # 全角数字→半角数字
    text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    # 全角ハイフンや長音記号を半角ハイフンに統一
    text = re.sub("[ー−―]", "-", text)
    return text

@router.get("/login", response_class=HTMLResponse)
def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/show-card", response_class=HTMLResponse)
def show_card(request: Request, name: str = Form(...), address: str = Form(...)):
    worksheet = get_worksheet()
    records = worksheet.get_all_records()

    # 🔸 入力値を正規化
    input_name = normalize(name)
    input_address = normalize(address)

    for record in records:
        # 🔸 シート上の値も正規化
        record_name = normalize(record.get("会員名", ""))
        record_address = normalize(record.get("会員番号（丁目、番地、号）", ""))

        if record_name == input_name and record_address == input_address:
            # 🔸 電話番号の先頭に0を追加
            phone = str(record.get("電話番号"))
            phone = "0" + phone
            record["電話番号"] = phone  # 上書き

            return templates.TemplateResponse(
                "member_card.html",
                {"request": request, "member": record}
            )

    return HTMLResponse(content="❌ 会員情報が見つかりません", status_code=404)
