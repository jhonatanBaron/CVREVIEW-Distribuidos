-levantamos con " docker compose up -d --build"
- petición de prueba de carga  por ejemplo con :
    "curl -X POST http://localhost:8000/api/upload \
  -F "file=@/home/jhona/Escritorio/CVREVIEW-Distribuidos/CVS/4_White_and_Black_Tech_Professional_Resume.pdf" \
  -F "full_name=STELLE DARCY" \
  -F "email=example@example.com" \
  -F "position=UX DESIGNER"  "

    --> obtenemos --> {"cv_id":1,"status":"pendiente"}
    -->obtenemos V2 -->{"message":"CV recibido y enviado a procesamiento correctamente.","cv_id":5,"status_endpoint":"/api/status/5"} 
  --> con swagger --> http://localhost:8000/docs

-petición de para consultar estado
  curl http://localhost:8000/api/status/1
  curl http://localhost:8000/api/status/2 


-Levantamos RabbitMQ y entramos al panel en:
    http://localhost:15672
    Usuario/Contraseña: guest / guest.

