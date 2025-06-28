from pymongo import MongoClient
from datetime import datetime
import time

client = MongoClient("mongodb://localhost:27017/")
db = client.ocr_database
collection = db.results

def save_ocr_record(text: str, img_path: str = None, txt_path: str = None, parsed_data: dict = None, user_id: int = None):
    from pymongo import MongoClient

    client = MongoClient()  # או mongo://localhost:27017 אם תרצה מפורש
    db = client["ocr_db"]
    collection = db["receipts"]

    timestamp = int(datetime.now().timestamp())
    
    record = {
        "text": text,
        "img_path": img_path,
        "txt_path": txt_path,
        "timestamp": timestamp,
        "parsed_data": parsed_data or {},
        "user_id": user_id
    }

    result = collection.insert_one(record)
    print(f"💾 Saved record to DB with _id: {result.inserted_id}")