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

Always return a JSON object with a fixed and complete structure, even if some values are missing. Do not omit fields – instead, use an empty string (""), zero (0), or an empty array ([]) depending on the expected type.
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
    "customer_phone": ""
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


#  ========================================

prompt = f"""
You will receive raw JSON from Google Document AI representing a scanned receipt or invoice.

Extract the following fields and return a structured JSON object using **snake_case** keys.

➡️ Always use the full structure shown below.  
✅ If data exists — extract it accurately.  
❌ Only use empty strings (""), 0, or [] when values are **truly missing**.  
Do not skip any fields or change the structure.

Fields:
1. biz_details: business_name, business_address (if available), vat_number (ח.פ or ת.ז)
2. transaction_time: purchase_date (YYYY-MM-DD), purchase_time (HH:MM if available)
3. customer: customer_name, customer_phone, membership_status (if inferrable)
4. receipt_number
5. total_amount
6. payment_method (cash, credit card, digital wallet, other)
7. total_vat_amount
8. products[]: product_name, quantity, unit_price, total_price

Here is the raw input:
{json.dumps(cleaned_data, ensure_ascii=False)}

Return JSON using this exact structure (fill with real values when possible):
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