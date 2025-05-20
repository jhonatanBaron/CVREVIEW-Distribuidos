from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.cv_model import Base, CVRequest
from api.config import settings

# Crear engine y sesión
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear las tablas si no existen
def init_db():
    Base.metadata.create_all(bind=engine)

# Función para guardar solicitud de CV
def save_cv_request(cv_id, nombre, email, puesto, filename):
    db = SessionLocal()
    try:
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
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
