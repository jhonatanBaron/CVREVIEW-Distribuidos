from sqlalchemy import Column, Integer, String, Text, Boolean
from database import Base

class CV(Base):
    __tablename__ = "cvs"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    content = Column(Text)
    is_valid_cv = Column(Boolean)
