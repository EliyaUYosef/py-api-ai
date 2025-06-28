import os
import io
from datetime import datetime
from PIL import Image
from .db import save_ocr_record
from .docai_extractor import save_docai_response
from .docai_parser import parse_receipt_with_docai
from .gpt_parser import parse_docai_json_with_gpt 
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.join(os.path.dirname(__file__), "../logs/images")
os.makedirs(BASE_DIR, exist_ok=True)

def extract_text_from_file(file_bytes: bytes, filename: str, content_type: str, user_id: int) -> dict:
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = os.path.splitext(filename)[1] or ".bin"
        file_name = f"{user_id}_{timestamp}{extension}"
        file_path = os.path.join(BASE_DIR, file_name)

        # שמירת הקובץ
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # 🧠 טיפול בקובץ טקסט (txt)
        if content_type == "text/plain":
            text = file_bytes.decode("utf-8")
            parsed_data = parse_docai_json_with_gpt({"text": text}, user_id=user_id, timestamp=timestamp)

        else:
            # תומך גם ב-pdf וגם בתמונה
            parsed_data = parse_receipt_with_docai(
                file_path=file_path,
                project_id=os.getenv("GOOGLE_CLOUD_PROJECT_ID"),
                location=os.getenv("GOOGLE_CLOUD_LOCATION"),
                processor_id=os.getenv("GOOGLE_CLOUD_PROCESSOR_ID"),
            )
            save_docai_response(parsed_data, user_id=user_id, timestamp=timestamp)
            parsed_data = parse_docai_json_with_gpt(parsed_data, user_id=user_id, timestamp=timestamp,extension=extension)

        # שמירה למסד הנתונים
        if os.getenv("SAVE_TO_DB", "true").lower() == "true":
            save_ocr_record("", file_path, None, parsed_data, user_id=user_id)

        return parsed_data

    except Exception as e:
        print("🚨 OCR ERROR:", e)
        raise