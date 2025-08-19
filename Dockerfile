FROM python:3.11

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir --use-deprecated=legacy-resolver -r requirements.txt

ENV GOOGLE_APPLICATION_CREDENTIALS=/app/keys/docai-service-account.json

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]