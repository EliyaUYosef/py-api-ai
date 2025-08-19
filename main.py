# File: main.py
from datetime import datetime
from unittest import result
from fastapi import FastAPI, File, UploadFile, HTTPException

from utils.ocr import extract_text_from_file

app = FastAPI()

@app.post("/ocr/")
async def upload_receipt(file: UploadFile = File(...)):
    request_ts = int(datetime.now().timestamp())
    file_bytes = await file.read()
    file_extension = file.content_type
    if file_extension not in ["image/png", "image/jpeg", "application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    result = extract_text_from_file(file_bytes, file.filename, request_ts=request_ts)
    
    return {
        "status": True,
        "message": "success",
        "data": {
            "purchase_data": result,
            "ocr_request_timestamp": request_ts,
        }
    }


@app.get("/ping1")
async def ping():
    print("🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢")
    return {"status": True, "message": "pong"}