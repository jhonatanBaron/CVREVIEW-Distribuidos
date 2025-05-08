
import os
from fastapi import UploadFile

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_uploaded_file(file: UploadFile, cv_id: str) -> str:
    filename = f"{cv_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return file_path
