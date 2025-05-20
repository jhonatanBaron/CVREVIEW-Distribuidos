from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from api.database.database import SessionLocal
from api.models.cv_model import CVRequest

router = APIRouter()

@router.get("/status/{cv_id}")
def get_status(cv_id: str):
    """
    Consulta el estado actual de un CV por su ID.
    """
    db: Session = SessionLocal()
    try:
        cv_req = db.query(CVRequest).filter(CVRequest.cv_id == cv_id).first()
        if not cv_req:
            raise HTTPException(status_code=404, detail="CV no encontrado")
        return {
            "cv_id": cv_req.cv_id,
            "estado": cv_req.estado,
            "fecha_creacion": cv_req.fecha_creacion
        }
    finally:
        db.close()
