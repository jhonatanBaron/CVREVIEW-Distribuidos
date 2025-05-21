

### 1. Crear archivo __init__.py

# api/__init__.py
# (vacío, para reconocer api/ como paquete Python)
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Importaciones ajustadas al paquete `api`
from api.database import engine
from api.cv_model import Base
from api.routes.upload import router as upload_router
from api.routes.status import router as status_router

# Instancia de FastAPI con metadatos
app = FastAPI(
    title="CVFlow API",
    description="API para subir y procesar hojas de vida de forma asíncrona",
    version="1.0.0"
)

# Crear tablas en startup en lugar de en import para asegurar orden
@app.on_event("startup")
def on_startup():
    # Inicializar esquema de base de datos
    Base.metadata.create_all(bind=engine)

# Configurar CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers con prefijo /api
app.include_router(upload_router, prefix="/api")
app.include_router(status_router, prefix="/api")

# Punto de entrada de Uvicorn: uvicorn api.main:app --host 0.0.0.0 --port 8000
