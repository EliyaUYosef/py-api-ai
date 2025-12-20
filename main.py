# File: main.py
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
import httpx
import os
from utils.ocr import extract_text_from_file

app = FastAPI()

@app.post("/ocr/")
async def upload_receipt(file: UploadFile = File(...), request_id: int = Form(...)):
    if request_id <= 0:
        raise HTTPException(status_code=400, detail="request_id must be positive")

    request_ts = int(datetime.now().timestamp())
    file_bytes = await file.read()

    file_extension = file.content_type
    if file_extension not in ["image/png", "image/jpeg", "application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    result = extract_text_from_file(file_bytes, file.filename, request_ts=request_ts, request_id=request_id)
    
    return {
        "status": True,
        "message": "success",
        "data": {
            "purchase_data": result,
            "ocr_request_timestamp": request_ts,
            "request_id": request_id,
        }
    }

@app.post("/ocr/url/")
async def process_receipt_from_url(url: str = Form(...), request_id: int = Form(...)):
    if request_id <= 0:
        raise HTTPException(status_code=400, detail="request_id must be positive")
    """Process receipt from URL - downloads file and processes it"""
    try:
        request_ts = int(datetime.now().timestamp())
        
        print(f"🔗 [OCR URL] Processing URL: {url}")
        
        # Download file from URL
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30, follow_redirects=True)
            response.raise_for_status()
            
            file_content = response.content
            content_type = response.headers.get('content-type', '')
            
            print(f"📥 [OCR URL] Downloaded {len(file_content)} bytes, content-type: {content_type}")
            
            # Validate content type
            if content_type not in ["image/png", "image/jpeg", "application/pdf", "text/plain"]:
                raise HTTPException(status_code=400, detail=f"Unsupported content type: {content_type}")
            
            # Extract filename from URL or use default
            filename = os.path.basename(url.split('?')[0]) or "receipt.pdf"
            if not filename or '.' not in filename:
                # Determine extension from content type
                if 'pdf' in content_type:
                    filename = "receipt.pdf"
                elif 'jpeg' in content_type or 'jpg' in content_type:
                    filename = "receipt.jpg"
                elif 'png' in content_type:
                    filename = "receipt.png"
                else:
                    filename = "receipt.bin"
            
            print(f"📄 [OCR URL] Processing file: {filename}")
        
            # Process the file
            result = extract_text_from_file(file_content, filename, request_ts=request_ts, request_id=request_id)
            
            return {
                "status": True,
                "message": "success",
                "data": {
                    "purchase_data": result,
                    "ocr_request_timestamp": request_ts,
                    "request_id": request_id,
                    "source_url": url
                }
            }
            
    except httpx.RequestError as e:
        print(f"❌ [OCR URL] Download error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to download file from URL: {str(e)}")
    
    except httpx.HTTPStatusError as e:
        print(f"❌ [OCR URL] HTTP error: {e.response.status_code}")
        raise HTTPException(status_code=400, detail=f"HTTP error {e.response.status_code} when downloading file")
    
    except Exception as e:
        print(f"❌ [OCR URL] Processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file from URL: {str(e)}")


@app.get("/ping1")
async def ping():
    print("🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢")
    return {"status": "ok", "message": "OCR service is running"}

@app.get("/")
async def root():
    return {
        "message": "Receipt OCR Service",
        "endpoints": {
            "upload": "POST /ocr/ - Upload file directly",
            "url": "POST /ocr/url/ - Process file from URL",
            "ping": "GET /ping1 - Health check"
        }
    }