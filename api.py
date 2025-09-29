from fastapi import FastAPI, Request
import sqlite3
import json

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
        payload = json.dumps(body)
    except Exception:
        # Si no es JSON, leer como texto
        body = await request.body()
        payload = body.decode("utf-8")

    # Guardar en BD (como texto plano)
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO data (payload) VALUES (?)", (payload,))
    conn.commit()
    conn.close()

    # Mostrar en terminal
    print("Nueva petición recibida:", payload)

    return {"status": "ok", "received": payload}
