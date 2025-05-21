from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from api.database.database import SessionLocal
from api.models.cv_model import CVRequest
import json

router = APIRouter()

@router.get("/keywords/{cv_id}")
def get_keywords(cv_id: str):
    """
    Devuelve la lista de keywords extraídas para un CV.
    """
    db: Session = SessionLocal()
    try:
        cv_req = db.query(CVRequest).filter(CVRequest.cv_id == cv_id).first()
        if not cv_req:
            raise HTTPException(status_code=404, detail="CV no encontrado")
        if not cv_req.keywords:
            raise HTTPException(status_code=404, detail="Keywords aún no generadas")
        return {
            "cv_id": cv_req.cv_id,
            "keywords": json.loads(cv_req.keywords)
        }
    finally:
        db.close()
