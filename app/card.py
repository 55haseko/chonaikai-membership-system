from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.sheets import get_worksheet

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
def show_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/show-card", response_class=HTMLResponse)
def show_card(request: Request, name: str = Form(...), address: str = Form(...)):
    worksheet = get_worksheet()
    records = worksheet.get_all_records()

    for record in records:
        if (
            record.get("会員名") == name and
            record.get("会員番号（丁目、番地、号）") == address
        ):
            # 👇 ここで電話番号の先頭に0を足すだけ
            phone = str(record.get("電話"))
            phone = "0" + phone
            record["電話"] = phone  # 上書き

            return templates.TemplateResponse(
                "member_card.html",
                {"request": request, "member": record}
            )

    return HTMLResponse(content="❌ 会員情報が見つかりません", status_code=404)
