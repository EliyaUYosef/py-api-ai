# utils/gpt_parser.py
import json
import os
import re
from datetime import datetime
from openai import OpenAI
from utils.cleaner import clean_docai_json_for_file_request, clean_docai_json_for_image_request  # ודא שהקובץ קיים
from utils.docai_extractor import save_docai_response  # ודא שהקובץ קיים

from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_prompt_template() -> str:
    with open("prompt_template.txt", "r", encoding="utf-8") as f:
        return f.read()

def load_template_structure() -> dict:
    with open("gpt_answer_structure.json", "r", encoding="utf-8") as f:
        return json.load(f)

def get_unix_timestamp(purchase_date: str, purchase_time: str | None = None) -> int:
    if not purchase_time or purchase_time.lower() == "none":
        dt = datetime.strptime(purchase_date, "%Y-%m-%d")
    else:
        dt = datetime.strptime(f"{purchase_date} {purchase_time}", "%Y-%m-%d %H:%M")
    return int(dt.timestamp())

def parse_docai_json_with_gpt(docai_data: dict, safe_file_name: str) -> dict:
    
    cleaned_data = clean_docai_json_for_file_request(docai_data)

    # template of gpt answer - json structure
    expected_structure = load_template_structure() # טען את מבנה התבנית מהקובץ JSON

    template = load_prompt_template() # טען את הפרומפט
    
    prompt = template.replace("{{cleaned_data}}", json.dumps(cleaned_data, ensure_ascii=False))
    prompt = prompt.replace("{{template_structure}}", json.dumps(expected_structure, ensure_ascii=False))

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
    
        save_docai_response(content, safe_file_name=safe_file_name, directory="logs/gpt_responses")
        
        return parsed_json
    except Exception as e:
        print("🧨 שגיאה בפענוח תגובת GPT:", e)
        return {"error": "Parsing failed"}
    
