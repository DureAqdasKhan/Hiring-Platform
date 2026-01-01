import os
import uuid
from fastapi import UploadFile

UPLOAD_DIR = "uploads"

def save_upload(file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1].lower()
    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path
