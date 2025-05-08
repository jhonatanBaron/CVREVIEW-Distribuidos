from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from uuid import uuid4
from services.parser import save_uploaded_file
from database.database import save_cv_request
import os

router = APIRouter()

@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),
    nombre: str = Form(...),
    email: str = Form(...),
    puesto: str = Form(...)
):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Formato no soportado. Solo PDF o DOCX")

    cv_id = str(uuid4())
    file_path = await save_uploaded_file(file, cv_id)

    save_cv_request(cv_id=cv_id, nombre=nombre, email=email, puesto=puesto, filename=file_path)

    return {"message": "CV recibido", "cv_id": cv_id}
