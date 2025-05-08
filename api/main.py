from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.upload import router as upload_router

app = FastAPI(
    title="CVFlow API",
    description="API para recibir y registrar hojas de vida",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # puedes limitarlo en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(upload_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "CVFlow API está corriendo"}
@app.get("/health")
def health_check():
    return {"status": "healthy"}
@app.get("/version")
def version():
    return {"version": "1.0.0"}
@app.get("/docs")
def docs():
    return {"message": "Documentación de la API"}
@app.get("/redoc")
def redoc():
    return {"message": "Documentación de la API en formato ReDoc"}
@app.get("/openapi.json")
def openapi():
    return {"message": "Especificación OpenAPI"}
@app.get("/openapi.yaml")
def openapi_yaml():
    return {"message": "Especificación OpenAPI en formato YAML"}
@app.get("/api/v1")
def api_v1():
    return {"message": "API v1"}
@app.get("/api/v1/health")
def api_v1_health():
    return {"status": "healthy"}
@app.get("/api/v1/version")
def api_v1_version():
    return {"version": "1.0.0"}
@app.get("/api/v1/docs")
def api_v1_docs():
    return {"message": "Documentación de la API v1"}
@app.get("/api/v1/redoc")
def api_v1_redoc():
    return {"message": "Documentación de la API v1 en formato ReDoc"}
@app.get("/api/v1/openapi.json")
def api_v1_openapi():
    return {"message": "Especificación OpenAPI de la API v1"}