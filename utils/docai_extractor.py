# utils/docai_extractor.py
import os
from utils.s3_utils import upload_to_s3

def save_docai_response(doc: dict, safe_file_name: str,directory="logs/docai_responses") -> str:
    """
    שומר את הפלט הגולמי של Google DocAI כקובץ JSON ומחזיר את הנתיב לקובץ או ל-S3.
    """
    filename = f"{safe_file_name}_file.json"
    local_path = os.path.join(directory, filename)

    if os.getenv("UPLOAD_TO_S3", "false").lower() == "true":
        s3_key = f"{directory}/{filename}"
        upload_to_s3(local_path, s3_key)
        print(f"📄 Google DocAI response uploaded to S3: {s3_key}")

    return local_path
