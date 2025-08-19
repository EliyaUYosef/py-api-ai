# utils/docai_extractor.py
import os
import json
from datetime import datetime
from utils.s3_utils import upload_to_s3

def save_docai_response(doc: dict, timestamp: str, directory="logs/docai_responses") -> str:
    """
    שומר את הפלט הגולמי של Google DocAI כקובץ JSON ומחזיר את הנתיב לקובץ או ל-S3.
    """
    filename = f"logs/{timestamp}_file.json"
    local_path = os.path.join(directory, filename)

    if os.getenv("LOCAL_DEBUG_MODE", "false").lower() == "true":
        os.makedirs(directory, exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)

    if os.getenv("DEBUG_MODE", "false").lower() == "true":
        s3_key = f"{directory}/{filename}"
        upload_to_s3(local_path, s3_key)
        os.remove(local_path)
        print(f"📄 Google DocAI response uploaded to S3: {s3_key}")

    print(f"📄 Google DocAI response saved to: {local_path}")
    return local_path
