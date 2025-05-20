from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class CVRequest(Base):
    __tablename__ = "cv_requests"

    cv_id = Column(String, primary_key=True)
    nombre = Column(String)
    email = Column(String)
    puesto = Column(String)
    filename = Column(String)
    estado = Column(String, default="pendiente")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CVRequest(cv_id={self.cv_id}, email={self.email}, estado={self.estado})>"
