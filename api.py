from fastapi import FastAPI, Request
import sqlite3
import json
from datetime import datetime
import logging

logger = logging.getLogger("uvicorn")

app = FastAPI()

# Crear BD y tabla si no existen
def init_db():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payload TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

@app.post("/captura")
async def receive_data(request: Request):
    try:
        # Intentar leer como JSON
        body = await request.json()

        # Asegurar que sea diccionario
        if isinstance(body, dict):
            # Crear timestamp con fecha + hora + milisegundos
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            body["timestamp"] = timestamp

        payload = json.dumps(body, ensure_ascii=False)

    except Exception:
        # Si no es JSON, leer como texto plano
        body = await request.body()
        payload = body.decode("utf-8")

    # Guardar en BD
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO data (payload) VALUES (?)", (payload,))
    conn.commit()
    conn.close()

    # Mostrar en terminal con logging
    logger.info(f"Nueva petición recibida: {payload}")

    return {"status": "ok", "received": payload}