# utils/ocr.py
import os
from .docai_extractor import save_docai_response
from .docai_parser import parse_receipt_with_docai
from .gpt_parser import parse_docai_json_with_gpt 
from dotenv import load_dotenv

BASE_DIR = os.path.join(os.path.dirname(__file__), "../logs/images")
os.makedirs(BASE_DIR, exist_ok=True)

def extract_text_from_file(file_bytes: bytes, filename: str, request_ts: int, request_id: int) -> dict:
    try:
        extension = os.path.splitext(filename)[1] or ".bin"
        file_name = f"{request_ts}_{request_id}_{extension}"
        file_path = os.path.join(BASE_DIR, file_name)

        # יצירת תיקייה בלבד אם לא קיימת
        os.makedirs(BASE_DIR, exist_ok=True)

        # שמירת הקובץ
        with open(file_path, "wb") as f:
            f.write(file_bytes)
            print(f"📥 File saved locally to: {file_path}")      

        load_dotenv()          
        # תומך גם ב-pdf וגם בתמונה
        parsed_data = parse_receipt_with_docai(
            file_path=file_path,
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT_ID"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),
            processor_id=os.getenv("GOOGLE_CLOUD_PROCESSOR_ID"),
        )
        safe_file_name=f"{request_ts}_{request_id}"
        save_docai_response(parsed_data, safe_file_name=safe_file_name)
        parsed_data = parse_docai_json_with_gpt(parsed_data, safe_file_name=safe_file_name)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ File removed: {file_path}")
        
        return parsed_data

    except Exception as e:
        print("🚨 OCR ERROR:", e)
        raise