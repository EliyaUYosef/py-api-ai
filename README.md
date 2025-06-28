# Receipt OCR & Parser Service

A Python-based backend microservice for extracting and structuring receipt/invoice data from images using Google Document AI and GPT (for JSON post-processing).

---

## 🧠 Features

* Upload an image of a receipt (PNG, JPG)
* Process the receipt using Google Document AI
* Use GPT to structure the extracted data
* Categorizes the receipt and detects payment method
* Save results in a MongoDB database (optional)
* Logs and responses are saved for debugging and tracking

---

## 🚀 Setup Instructions

### 1. Clone the repository

```bash
git clone <repo-url>
cd <project-folder>
```

### 2. Run the setup script

```bash
./run.sh
```

This will:

* Create a virtual environment (if not exists)
* Install dependencies
* Activate the environment
* Set Google Cloud credentials
* Start the FastAPI development server

### 3. Google Cloud Configuration

Ensure you have a valid Document AI processor and service account credentials in:

```
keys/docai-service-account.json
```

Update your `.env` file accordingly:

```ini
GOOGLE_CLOUD_PROJECT_ID=your_project_id
GOOGLE_CLOUD_LOCATION=us
GOOGLE_CLOUD_PROCESSOR_ID=your_processor_id
OPENAI_API_KEY=sk-...
SAVE_TO_DB=true
```

---

## 🖼️ OCR Endpoint

### POST `/ocr/`

**Request**: Multipart form-data with image file
**Optional query params**:

* `use_docai=true` to use Google Document AI

**Response**:

```json
{
  "status": true,
  "message": "success",
  "parsed_data": {
    "biz_details": {...},
    "transaction_time": {...},
    "products": [...],
    ...
  }
}
```

---

## 📁 Output Fields

* `biz_details`: Name, address, and VAT number of the business
* `transaction_time`: Date and time of purchase
* `customer`: Optional customer details
* `category`: Category of the purchase (e.g., Groceries, Car maintenance)
* `receipt_number`
* `total_amount`
* `payment_method`: Cash, credit, digital wallet, etc.
* `total_vat_amount`
* `products`: List of products with name, quantity, unit price, and total price

---

## 📂 Folder Structure

```
utils/
 ├── cleaner.py
 ├── docai_extractor.py
 ├── docai_parser.py
 ├── gpt_parser.py
 └── db.py
main.py
run.sh
requirements.txt
README.md
logs/
saved_ocr/
```

---

## ✅ How to Run (Manual)

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the server:

```bash
uvicorn main:app --reload
```

3. POST a receipt image to:

```
POST /ocr/
Content-Type: multipart/form-data
Field: image=<your_image_file>
```

---

## 📃 Logs

* Raw Google DocAI responses: `logs/docai_responses/`
* GPT structured responses: `logs/gpt_responses/`

---

## 📌 TODO (Next Steps)

* [ ] Frontend uploader UI
* [ ] Webhook integration or frontend sync
* [ ] Category stats & visual reports
* [ ] User-based filtering and login

---

## 📆 License

MIT

---

> Created with ❤️ by Eliya
