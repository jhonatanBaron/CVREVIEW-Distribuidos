from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models.cv_model import CV
from services.parser import extract_text_from_pdf
from utils.validate_cv import is_valid_cv

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload")
async def upload_cv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    text = extract_text_from_pdf(file)
    valid = is_valid_cv(text)

    cv = CV(filename=file.filename, content=text, is_valid_cv=valid)
    db.add(cv)
    db.commit()
    db.refresh(cv)

    return {"cv_id": cv.id, "valid": valid}
