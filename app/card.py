from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.sheets import get_worksheet
import re
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# 🔹 表記揺れ補正関数
def normalize(text: str) -> str:
    if not text:
        return ""
    text = text.replace(" ", "").replace("　", "")
    text = text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    text = re.sub("[ー−―]", "-", text)
    return text

# 🔹 最終有効年度を計算
def get_last_valid_year(payment_date_str: str, paid_years: int) -> int:
    if not payment_date_str or not paid_years:
        return 0
    try:
        payment_date = datetime.strptime(payment_date_str, "%Y/%m/%d")
        if payment_date.month >= 4:
            start_year = payment_date.year
        else:
            start_year = payment_date.year - 1
        last_valid_year = start_year + paid_years - 1
        return last_valid_year
    except Exception:
        return 0

# 🔹 有効期限日を計算
def get_expiration_date(payment_date_str: str, paid_years: int) -> str:
    if not payment_date_str or not paid_years:
        return "未納"
    try:
        payment_date = datetime.strptime(payment_date_str, "%Y/%m/%d")
        if payment_date.month >= 4:
            start_year = payment_date.year
        else:
            start_year = payment_date.year - 1
        last_year = start_year + paid_years - 1
        expiration_date = datetime(last_year + 1, 3, 31).strftime("%Y/%m/%d")
        return expiration_date
    except Exception:
        return "未納"

@router.get("/login", response_class=HTMLResponse)
def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/show-card", response_class=HTMLResponse)
def show_card(
    request: Request,
    name: str = Form(...),
    address: str = Form(...),
    phone: str = Form(None)
):
    worksheet = get_worksheet()
    records = worksheet.get_all_records()

    input_name = normalize(str(name))
    input_address = normalize(str(address))
    input_phone = normalize(str(phone or ""))

    # 🔸 名前+住所検索
    for record in records:
        record_name = normalize(str(record.get("会員名", "")))
        record_address = normalize(str(record.get("会員番号（丁目、番地、号）", "")))

        if record_name == input_name and record_address == input_address:
            phone_value = str(record.get("電話番号") or "")
            phone_value = "0" + phone_value if phone_value else "（未登録）"
            record["電話番号"] = phone_value

            paid_years = int(record.get("今年からの会費納入回数") or 0)
            last_year = get_last_valid_year(record.get("会費納入日"), paid_years)
            expiration_date = get_expiration_date(record.get("会費納入日"), paid_years)

            record["有効期限年度"] = last_year if last_year else "未納"
            record["有効期限日"] = expiration_date

            current_year = datetime.now().year
            current_month = datetime.now().month
            current_fiscal_year = current_year if current_month >= 4 else current_year - 1

            if (not last_year) or (last_year < current_fiscal_year):
                return templates.TemplateResponse("unpaid.html", {"request": request, "member": record})

            return templates.TemplateResponse("member_card.html", {"request": request, "member": record})

    # 🔸 電話番号未入力 → 電話番号入力を促す画面へ
    if not phone:
        return templates.TemplateResponse(
            "retry_with_phone.html",
            {"request": request, "name": name, "address": address}
        )

    # 🔸 電話番号を含めた再検索
    for record in records:
        record_name = normalize(str(record.get("会員名", "")))
        record_address = normalize(str(record.get("会員番号（丁目、番地、号）", "")))
        record_phone = normalize(str(record.get("電話番号") or ""))

        if record_name == input_name and record_address == input_address and record_phone == input_phone:
            phone_value = str(record.get("電話番号") or "")
            phone_value = "0" + phone_value if phone_value else "（未登録）"
            record["電話番号"] = phone_value

            paid_years = int(record.get("今年からの会費納入回数") or 0)
            last_year = get_last_valid_year(record.get("会費納入日"), paid_years)
            expiration_date = get_expiration_date(record.get("会費納入日"), paid_years)

            record["有効期限年度"] = last_year if last_year else "未納"
            record["有効期限日"] = expiration_date

            current_year = datetime.now().year
            current_month = datetime.now().month
            current_fiscal_year = current_year if current_month >= 4 else current_year - 1

            if (not last_year) or (last_year < current_fiscal_year):
                return templates.TemplateResponse("unpaid.html", {"request": request, "member": record})

            return templates.TemplateResponse("member_card.html", {"request": request, "member": record})

    # 🔸 最後に電話番号だけ一致する場合に部分情報表示
    for record in records:
        record_phone = normalize(str(record.get("電話番号") or ""))
        if record_phone == input_phone:
            partial_info = {
                "会員名": record.get("会員名", "")[:1] + "＊＊＊",
                "住所": record.get("会員番号（丁目、番地、号）", "")[:3] + "＊＊＊",
                "電話番号": "0" + str(record.get("電話番号"))
            }
            return templates.TemplateResponse(
                "partial_info.html",
                {"request": request, "member": partial_info}
            )

    # 🔸 それでも見つからない場合
    return templates.TemplateResponse("not_found.html", {"request": request})
