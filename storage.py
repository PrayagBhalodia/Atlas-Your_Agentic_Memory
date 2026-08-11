"""S3 storage for uploaded source documents (ingestion staging). [Track B]

The ingestion path stages the raw uploaded file in S3 before it's distilled into memory,
so the original source is kept (provenance + reprocessing). S3 is plain storage — not
Bedrock/Marketplace — so it runs on the AWS free credit with no card.

Bucket: S3_BUCKET in .env if set, otherwise auto-derived as atlas-docs-<accountId>.
The bucket is created automatically on first upload if it doesn't exist.
Needs: AWS creds in .env (already present) + S3 permission on the IAM user (AmazonS3FullAccess).
"""
import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

_REGION = os.getenv("AWS_REGION", "us-east-1")


def is_configured() -> bool:
    """S3 is available if AWS credentials are present (bucket is auto-derived/created)."""
    return bool(os.getenv("AWS_ACCESS_KEY_ID"))


def _bucket_name() -> str:
    name = os.getenv("S3_BUCKET")
    if name:
        return name
    account = boto3.client("sts", region_name=_REGION).get_caller_identity()["Account"]
    return f"atlas-docs-{account}"


def _ensure_bucket(client, bucket: str) -> None:
    try:
        client.head_bucket(Bucket=bucket)
        return  # already exists and we own it
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") not in ("404", "NoSuchBucket"):
            raise  # 403 (owned by someone else) or other -> surface it
    if _REGION == "us-east-1":
        client.create_bucket(Bucket=bucket)  # us-east-1 must NOT send a LocationConstraint
    else:
        client.create_bucket(Bucket=bucket,
                              CreateBucketConfiguration={"LocationConstraint": _REGION})


def upload_document(name: str, data: bytes) -> str:
    """Store the original uploaded file in S3 under uploads/<timestamp>_<name>.
    Creates the bucket if needed. Returns the s3:// URI. Raises on a real S3 error."""
    bucket = _bucket_name()
    client = boto3.client("s3", region_name=_REGION)
    _ensure_bucket(client, bucket)
    key = f"uploads/{datetime.now(timezone.utc):%Y%m%dT%H%M%S}_{name}"
    client.put_object(Bucket=bucket, Key=key, Body=data)
    return f"s3://{bucket}/{key}"
