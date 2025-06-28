from fastapi import FastAPI, File, UploadFile
from utils.ocr import extract_text_from_file

app = FastAPI()
sample_user = {
    "user_id": "1",
    "name": "Eliya Yosef",
}

@app.post("/ocr/")
async def upload_receipt(file: UploadFile = File(...)):
    file_bytes = await file.read()
    content_type = file.content_type

    if content_type not in ["image/png", "image/jpeg", "application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    parsed_data = extract_text_from_file(file_bytes, file.filename, content_type, user_id=sample_user["user_id"])
    
    return {
        "status": True,
        "message": "success",
        "parsed_data": parsed_data
    }