from fastapi import FastAPI
from models.cv_model import Base
from database import engine
from routes import upload

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(upload.router)
