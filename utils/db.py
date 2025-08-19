import os
from pymongo import MongoClient
from datetime import datetime

mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(mongo_uri)
db = client.ocr_db
collection = db.receipts


def save_ocr_record(text: str, img_path: str = None, txt_path: str = None, parsed_data: dict = None, user_id: int = None):

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