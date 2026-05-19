from fastapi import FastAPI
from pydantic import BaseModel
from services.ai import generar_respuesta
from database import guardar_interaccion #Modificacion 1 Importamos el puente de la base de datos

app = FastAPI()

# Modelo de datos (estructura del JSON)
class Mensaje(BaseModel):
    usuario: str #Modificacion 2 Agregamos el campo usuario al modelo de datos
    mensaje: str

# Endpoint webhook
@app.post("/webhook")
async def webhook(data: Mensaje):
    
    respuesta = generar_respuesta(data.mensaje)

    print("Mensaje recibido:", data.mensaje)
    print("Respuesta IA:", respuesta)
    #Modificacion 3 Ejecutar el guardado real en tu SQLite
    guardar_interaccion(data.usuario, data.mensaje, respuesta)

    return {
        "respuesta": respuesta
    }
