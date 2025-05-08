# api/database/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.cv_model import Base, CVRequest
import os

# Leer la URL desde variable de entorno (por defecto PostgreSQL local)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cvuser:cvpass@postgres_cvflow:5432/cvflow")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def save_cv_request(cv_id, nombre, email, puesto, filename):
    db = SessionLocal()
    new_cv = CVRequest(
        cv_id=cv_id,
        nombre=nombre,
        email=email,
        puesto=puesto,
        filename=filename,
        estado="pendiente"
    )
    db.add(new_cv)
    db.commit()
    db.close()
