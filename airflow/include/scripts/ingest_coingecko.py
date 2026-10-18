import json
import logging
from datetime import datetime
import os
import requests
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT_URL", "http://localhost:9000")
ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadminpassword")
BUCKET_NAME = os.getenv("MINIO_BUCKET_BRONZE", "bronze")
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1"

def fetch_and_load_coingecko_data():
    """
    Extracts top 100 cryptocurrency market metrics from CoinGecko public API
    and persists raw JSON output into MinIO S3 Bronze bucket partitioned by date.
    """
    logging.info("Initiating CoinGecko API extraction...")
    headers = {"User-Agent": "AnalyticsEnginePipeline/1.0"}
    
    try:
        response = requests.get(COINGECKO_URL, headers=headers, timeout=20)
        response.raise_for_status()
        raw_payload = response.json()
        logging.info("Successfully fetched %d records from API.", len(raw_payload))
    except requests.exceptions.RequestException as exc:
        logging.error("Failed to fetch data from CoinGecko API: %s", exc)
        raise

    s3_client = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )

    try:
        existing_buckets = [b["Name"] for b in s3_client.list_buckets().get("Buckets", [])]
        if BUCKET_NAME not in existing_buckets:
            s3_client.create_bucket(Bucket=BUCKET_NAME)
            logging.info("Created missing MinIO bucket: %s", BUCKET_NAME)
    except ClientError as exc:
        logging.error("Error verifying/creating MinIO bucket: %s", exc)
        raise

    execution_date = datetime.now().strftime("%Y-%m-%d")
    object_key = f"crypto_markets/{execution_date}/top100_coins.json"

    try:
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=object_key,
            Body=json.dumps(raw_payload),
            ContentType="application/json"
        )
        logging.info("Raw JSON successfully loaded to s3://%s/%s", BUCKET_NAME, object_key)
    except ClientError as exc:
        logging.error("Failed uploading JSON payload to MinIO: %s", exc)
        raise

if __name__ == "__main__":
    fetch_and_load_coingecko_data()