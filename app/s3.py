# app/s3.py
import os
import boto3
from botocore.client import Config
from urllib.parse import quote

AWS_REGION = os.getenv("AWS_REGION", "eu-north-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
S3_PREFIX = os.getenv("S3_PREFIX", "applications")
S3_PRESIGN_EXPIRES_SECONDS = int(os.getenv("S3_PRESIGN_EXPIRES_SECONDS", "60"))
sts = boto3.client("sts")

if not S3_BUCKET_NAME:
    raise RuntimeError("S3_BUCKET_NAME is not set")

_s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    config=Config(signature_version="s3v4"),
)

def build_cv_key(application_id: str, filename: str) -> str:
    safe_name = filename.replace("/", "_").replace("\\", "_")
    return f"{S3_PREFIX}/{application_id}/cv/{safe_name}"

def upload_cv_file(fileobj, key: str, content_type: str | None = None):
    extra = {}
    if content_type:
        extra["ContentType"] = content_type

    _s3.upload_fileobj(
        Fileobj=fileobj.file,
        Bucket=S3_BUCKET_NAME,
        Key=key,
        ExtraArgs=extra,
    )

def presign_get_url(key: str, download_name: str | None = None) -> str:
    params = {"Bucket": S3_BUCKET_NAME, "Key": key}

    # Optional: force a download filename (nicer UX)
    if download_name:
        safe = download_name.replace('"', "")
        params["ResponseContentDisposition"] = f'attachment; filename="{safe}"'
        # Optional: if you want, you can also set ResponseContentType

    return _s3.generate_presigned_url(
        ClientMethod="get_object",
        Params=params,
        ExpiresIn=S3_PRESIGN_EXPIRES_SECONDS,
    )
