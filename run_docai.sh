#!/bin/bash

cd "$(dirname "$0")"

# יצירת סביבה וירטואלית אם צריך
if [ ! -d "venv" ]; then
    echo "📦 No virtual environment found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "✅ Virtual environment found."
    source venv/bin/activate
fi

# משתנה הרשאות ל-Google Cloud
export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/keys/docai-service-account.json"
echo "🔐 GOOGLE_APPLICATION_CREDENTIALS set to $GOOGLE_APPLICATION_CREDENTIALS"

# הרצת שרת FastAPI
uvicorn main:app --reload