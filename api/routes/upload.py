from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from uuid import uuid4
from api.shared.queue_config import get_channel
from services.parser import save_uploaded_file
from database.database import save_cv_request
import json
import pika 

#el objetivo es recibir un CV y guardarlo en la base de datos
router = APIRouter()

@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),
    nombre: str = Form(...),
    email: str = Form(...),
    puesto: str = Form(...)
):
    if not file.filename.endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail="Formato no soportado. Solo PDF o DOCX")

    cv_id = str(uuid4())
    file_path = await save_uploaded_file(file, cv_id)

    # Guardar en DB
    save_cv_request(cv_id=cv_id, nombre=nombre, email=email, puesto=puesto, filename=file_path)

    # Enviar mensaje a RabbitMQ
    #encolar el mensaje en la cola parser_queue
    # el mensaje contiene el id del cv, el nombre del archivo y el email
    try:
        channel, conn = get_channel()
        payload = {
            "cv_id": cv_id,
            "filename": file_path,
            "email": email
        }
        channel.basic_publish(
            exchange='',
            routing_key='parser_queue',
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2)  # persistente
        )
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encolando mensaje: {str(e)}")

    return {"message": "CV recibido", "cv_id": cv_id}
