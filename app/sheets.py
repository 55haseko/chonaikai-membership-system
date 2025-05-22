import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def get_worksheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDENTIALS_JSON"), scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv("SPREADSHEET_KEY"))
    worksheet = sheet.worksheet("Sheet1")  # シート名を指定
    return worksheet

def find_member_by_line_id(line_user_id: str):
    worksheet = get_worksheet()
    records = worksheet.get_all_records()
    for record in records:
        if record.get("line_id") == line_user_id:
            return record
    return None
