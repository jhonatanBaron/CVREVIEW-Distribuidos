#api/routes/upload.py
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from api.cv_model import CV
from api.database import SessionLocal
from api.rabbitmq import publish_to_parser_queue
import os

router = APIRouter()

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
    if not file.filename.endswith((".pdf", ".docx", ".doc")):
        raise HTTPException(status_code=400, detail="Archivo no válido. Debe ser PDF o Word.")

    cv_id = str(uuid4())

    cv = CV(
        #id=None,
        filename=file.filename,
        full_name=full_name,
        email=email,
        position=position,
        status="pendiente"
    )
    db.add(cv)
    db.commit()
    db.refresh(cv)

    message = {
    "cv_id": cv.id,
    "email": email,
    "filename": file.filename  
    }
    publish_to_parser_queue(message)

  #  return {"cv_id": cv.id, "status": "pendiente"}
    return {
    "message": "CV recibido y enviado a procesamiento correctamente.",
    "cv_id": cv.id,
    "status_endpoint": f"/api/status/{cv.id}"
    }
