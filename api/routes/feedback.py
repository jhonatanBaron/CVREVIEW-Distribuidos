from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from api.database.database import SessionLocal
from api.models.cv_model import CVRequest
import json

router = APIRouter()

@router.get("/feedback/{cv_id}")
def get_feedback(cv_id: str):
    """
    Devuelve las sugerencias de feedback y la puntuación del CV.
    """
    db: Session = SessionLocal()
    try:
        cv_req = db.query(CVRequest).filter(CVRequest.cv_id == cv_id).first()
        if not cv_req:
            raise HTTPException(status_code=404, detail="CV no encontrado")
        if not cv_req.feedback:
            raise HTTPException(status_code=404, detail="Feedback aún no generado")
        return {
            "cv_id": cv_req.cv_id,
            "feedback": json.loads(cv_req.feedback),
            "score": cv_req.score
        }
    finally:
        db.close()
