# api/routes/upload.py
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from api.cv_model import CV
from api.database import SessionLocal
from api.rabbitmq import publish_to_parser_queue
from werkzeug.utils import secure_filename  # Para asegurar nombre de archivo
import os

router = APIRouter()

# Tamaño máximo permitido del archivo (5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024  

# Lista de posiciones válidas (puedes editar según tu proyecto)
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
    # Validar extensión del archivo
    if not file.filename.endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(status_code=400, detail="Archivo no válido. Debe ser PDF o Word.")

    # Validar tipo MIME del archivo
    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword"
    ]:
        raise HTTPException(status_code=400, detail="El tipo de archivo no es válido.")

    # Validar tamaño del archivo (leyéndolo parcialmente)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="El archivo supera el tamaño máximo permitido de 5 MB.")
    await file.seek(0)  # Reiniciar cursor del archivo para no afectar su posterior uso

    # Validar nombre completo (mínimo nombre y apellido)
    if len(full_name.strip().split()) < 2:
        raise HTTPException(status_code=400, detail="Por favor ingresa tu nombre completo.")

    # Validar que no exista una entrada previa con el mismo nombre y correo
    existing_cv = db.query(CV).filter(CV.full_name == full_name, CV.email == email).first()
    if existing_cv:
        raise HTTPException(status_code=400, detail="Ya se ha registrado un CV con este nombre y correo.")

    # Validar que la posición deseada sea válida
    if position not in VALID_POSITIONS:
        raise HTTPException(status_code=400, detail=f"Posición no válida. Usa una de: {', '.join(VALID_POSITIONS)}.")

    # Asegurar nombre del archivo (elimina rutas maliciosas, etc.)
    safe_filename = secure_filename(file.filename)

    # Crear un nuevo UUID para el CV
    cv_id = str(uuid4())

    # Crear instancia del modelo CV y guardar en base de datos
    cv = CV(
        filename=safe_filename,
        full_name=full_name,
        email=email,
        position=position,
        status="pendiente"
    )
    db.add(cv)
    db.commit()
    db.refresh(cv)

    # Enviar mensaje al worker parser vía RabbitMQ
    message = {
        "cv_id": cv.id,
        "email": email,
        "filename": safe_filename
    }
    publish_to_parser_queue(message)

    # Respuesta al cliente
    return {
        "message": "CV recibido y enviado a procesamiento correctamente.",
        "cv_id": cv.id,
        "status_endpoint": f"/api/status/{cv.id}"
    }
