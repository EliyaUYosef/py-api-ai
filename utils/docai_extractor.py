import os
import json
from datetime import datetime

def save_docai_response(doc: dict, user_id: int, timestamp: str, directory="logs/docai_responses") -> str:
    """
    שומר את הפלט הגולמי של Google DocAI כקובץ JSON ומחזיר את הנתיב לקובץ.
    """
    os.makedirs(directory, exist_ok=True)
    filename = f"{user_id}_{timestamp}.json"
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
        
    print(f"📄 Google DocAI response saved to: {path}")
    return path
