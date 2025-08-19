# File: utils/s3_utils.py
import boto3
import os
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

def upload_to_s3(file_path: str, s3_key: str):
    bucket_name = os.getenv("S3_BUCKET_NAME")
    try:
        s3.upload_file(file_path, bucket_name, s3_key)
        print("✅ File uploaded to S3")
        return f"s3://{bucket_name}/{s3_key}"
    except NoCredentialsError:
        print("⛔ AWS credentials missing!")
        return None