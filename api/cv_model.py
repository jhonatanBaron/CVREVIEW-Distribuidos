#api/cv_model.py
from sqlalchemy import Column, Integer, String, Text
from api.database import Base

class CV(Base):
    __tablename__ = "cvs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    full_name = Column(String)
    email = Column(String)
    position = Column(String)
    status = Column(String, default="pendiente")
