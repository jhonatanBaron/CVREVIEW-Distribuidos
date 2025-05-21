# api/routes/upload.py

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from api.cv_model import CV
from api.database import SessionLocal
from api.rabbitmq import publish_to_parser_queue
from werkzeug.utils import secure_filename  # Para sanear el nombre del archivo
import os
import shutil
import re

router = APIRouter()

# Tamaño máximo permitido del archivo (5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Lista de posiciones válidas
VALID_POSITIONS = {"Backend Developer", "Frontend Developer", "UX Designer", "Data Scientist"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),
    full_name: str = Form(...),
    email: str = Form(...),
    position: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Extensión y MIME
    if not file.filename.lower().endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(400, "Archivo no válido. Debe ser PDF o Word.")
    if file.content_type not in (
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ):
        raise HTTPException(400, "El tipo de archivo no es válido.")

    # 2. Tamaño
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "El archivo supera el tamaño máximo de 5 MB.")
    await file.seek(0)

    # 3. Datos de formulario
    if len(full_name.strip().split()) < 2:
        raise HTTPException(400, "Ingresa nombre y apellido.")
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        raise HTTPException(400, "Email con formato inválido.")
    if position not in VALID_POSITIONS:
        raise HTTPException(400, f"Posición no válida. Elige: {', '.join(VALID_POSITIONS)}.")

    # 4. Evitar duplicados
    exists = db.query(CV).filter(CV.full_name == full_name, CV.email == email).first()
    if exists:
        raise HTTPException(409, "Ya existe un CV con ese nombre y correo.")

    # 5. Sanear y guardar archivo
    safe_name = secure_filename(file.filename)
    upload_dir = "/files"
    os.makedirs(upload_dir, exist_ok=True)
    dest_path = os.path.join(upload_dir, safe_name)
    with open(dest_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

    # 6. Registrar en BD
    cv = CV(
        filename=safe_name,
        full_name=full_name,
        email=email,
        position=position,
        status="pendiente"
    )
    db.add(cv)
    db.commit()
    db.refresh(cv)

    # 7. Encolar mensaje para parser
    publish_to_parser_queue({
        "cv_id": cv.id,
        "email": email,
        "filename": safe_name
    })

    # 8. Respuesta
    return {
        "message": "CV recibido y enviado a procesamiento correctamente.",
        "cv_id": cv.id,
        "status_endpoint": f"/api/status/{cv.id}"
    }
    
    