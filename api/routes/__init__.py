from .upload import router as upload_router
from .status import router as status_router

# Exportar los routers para que sean accesibles cuando se importe routes
router = upload_router
status = status_router