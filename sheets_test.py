# sheets_test.py

from dotenv import load_dotenv
load_dotenv()

from app.sheets import get_worksheet

def main():
    try:
        ws = get_worksheet()
        print("✅ シート名:", ws.title)
        records = ws.get_all_records()
        print(f"✅ データ件数: {len(records)} 件")

        if records:
            print("📄 サンプル1件目:")
            print(records[0])
        else:
            print("⚠️ データがありません")

    except Exception as e:
        print("❌ エラー発生:", e)

if __name__ == "__main__":
    main()
