import json
import os
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from utils.cleaner import clean_docai_json_for_file_request, clean_docai_json_for_image_request  # ודא שהקובץ קיים
from utils.docai_extractor import save_docai_response  # ודא שהקובץ קיים

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_docai_json_with_gpt(docai_data: dict, user_id: int, timestamp: str, extension='text/plain') -> dict:
    # שלב הניקוי
    # נניח שכבר יש לך את extension, לדוגמה:
    # extension = os.path.splitext(filename)[1].lower() or ".bin"

    if extension in [".txt", ".text", ".plain", ".jpeg", ".pdf"]:
        cleaned_data = clean_docai_json_for_file_request(docai_data)
    else:
        cleaned_data = clean_docai_json_for_image_request(docai_data)
    # return cleaned_data

    prompt = f"""
ensure all field names in the returned JSON use just snake_case format.
If any of the requested fields are missing, skip them gracefully and continue with the rest without failing.
The following data is a raw JSON output from Google Document AI, representing a scanned receipt or invoice. Please process it and return a structured JSON object with the following fields:

1. **biz_details**:
   - Business name
   - Business address (if available)
   - VAT number or Company registration number (ח.פ או ת.ז)

2. **transaction_time**:
   - Purchase date (format: YYYY-MM-DD)
   - Purchase time (if available, format: HH:MM)

3. **customer** (only if customer details are available):
   - Customer name
   - Customer phone (if available)
   - Membership status (if it can be inferred)

4. **receipt_number** – The receipt number (if available)

5. **total_amount** – The total amount paid

6. **payment_method** – The payment method if available: cash, credit card, digital wallet, or other.

7. **total_vat_amount** – The total VAT amount (if available)

8. **products** – A list of purchased products, each with:
   - Product name
   - Quantity
   - Unit price
   - Total price

Here is the raw data:
{json.dumps(cleaned_data, ensure_ascii=False)}

Always return a JSON object with a fixed and complete structure.
{json.dumps({
  "biz_details": {
    "business_name": "",
    "business_address": "",
    "vat_number": ""
  },
  "transaction_time": {
    "purchase_date": "",
    "purchase_time": "",
    "unix_ts": 0
  },
  "customer": {
    "customer_name": "",
    "customer_phone": "",
    "membership_status": ""
  },
  "receipt_number": "",
  "total_amount": 0,
  "payment_method": "",
  "total_vat_amount": 0,
  "products": [
    {
      "product_name": "",
      "quantity": 0,
      "unit_price": 0,
      "total_price": 0
    }
  ]
}, ensure_ascii=False)}
"""

    try:
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "Extract structured data from receipt JSON"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2
        )
        
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\n*", "", content)  # מסיר את ההתחלה ```json\n
            content = re.sub(r"\n*```$", "", content)           # מסיר את הסיום \n```
            content = content.strip()  

        # אחרי הניקוי מ-```json ... ```
        parsed_json = json.loads(content)

        transaction_time = parsed_json.get("transaction_time", {})
        purchase_date = transaction_time.get("purchase_date")
        purchase_time = transaction_time.get("purchase_time", "00:00")  # ברירת מחדל לשעה

        if purchase_date:
            parsed_json["transaction_time"]["unix_ts"] = get_unix_timestamp(purchase_date, purchase_time)
        

        save_docai_response(content, user_id=user_id, timestamp=timestamp, directory="logs/gpt_responses")
        
        return parsed_json
    except Exception as e:
        print("🧨 שגיאה בפענוח תגובת GPT:", e)
        return {"error": "Parsing failed"}
    
def get_unix_timestamp(purchase_date: str, purchase_time: str | None = None) -> int:
    if not purchase_time or purchase_time.lower() == "none":
        dt = datetime.strptime(purchase_date, "%Y-%m-%d")
    else:
        dt = datetime.strptime(f"{purchase_date} {purchase_time}", "%Y-%m-%d %H:%M")
    return int(dt.timestamp())