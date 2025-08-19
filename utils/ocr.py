# utils/ocr.py
import os
import random
from datetime import datetime
from .db import save_ocr_record
from .docai_extractor import save_docai_response
from .docai_parser import parse_receipt_with_docai
from .gpt_parser import parse_docai_json_with_gpt 
from dotenv import load_dotenv
from .s3_utils import upload_to_s3

BASE_DIR = os.path.join(os.path.dirname(__file__), "../logs/images")
os.makedirs(BASE_DIR, exist_ok=True)

def extract_text_from_file(file_bytes: bytes, filename: str, request_ts: int) -> dict:
    try:
        extension = os.path.splitext(filename)[1] or ".bin"
        random_suffix = random.randint(1000, 9999)
        file_name = f"{request_ts}_{random_suffix}{extension}"
        file_path = os.path.join(BASE_DIR, file_name)

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

        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ File removed: {file_path}")

        save_docai_response(parsed_data, timestamp=request_ts)
        parsed_data = parse_docai_json_with_gpt(parsed_data, timestamp=request_ts)


        return parsed_data,

    except Exception as e:
        print("🚨 OCR ERROR:", e)
        raise