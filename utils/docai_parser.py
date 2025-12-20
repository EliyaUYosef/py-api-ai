# utils/docai_parser.py
import os
from google.cloud import documentai_v1 as documentai

def parse_receipt_with_docai(file_path: str, project_id: str, location: str, processor_id: str) -> dict:
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        raise EnvironmentError("❌ GOOGLE_APPLICATION_CREDENTIALS not set")

    client = documentai.DocumentProcessorServiceClient()
    print("✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅")
    print("✅ OCR process started successfully")
    processor_path = client.processor_path(project=project_id, location=location, processor=processor_id)

    with open(file_path, "rb") as file:
        file_content = file.read()

    mime_type = "application/pdf" if file_path.endswith(".pdf") else "image/png"
    print(f"✅ File MIME type set to: {mime_type}")
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
    print("✅ Raw document created")
    request = documentai.ProcessRequest(
        name=processor_path,
        raw_document=raw_document
    )
    print("✅ Process request created, sending to Document AI...")
    result = client.process_document(request=request)
    print("✅ Document AI processing complete")
    document = result.document
    print("✅ Document received from Document AI")

    # Convert Document to dict
    print("✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅ ✅")
    return documentai.Document.to_dict(document)

