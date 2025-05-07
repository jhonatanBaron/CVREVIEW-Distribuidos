from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from cv_model import Base
from routes import upload

# Crear la instancia principal de FastAPI
app = FastAPI(
    title="CVFlow API",
    description="API para subir y validar hojas de vida",
    version="1.0.0"
)

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)

# Habilitar CORS si estás probando desde frontend o Postman
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción puedes restringirlo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas definidas en routes/upload.py
app.include_router(upload.router)
