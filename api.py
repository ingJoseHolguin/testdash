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
    body = await request.json()
    
    # Guardar en BD
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO data (payload) VALUES (?)", (json.dumps(body),))
    conn.commit()
    conn.close()

    # Mostrar en terminal
    print("Nueva petición recibida:", body)

    return {"status": "ok", "received": body}


# pip install fastapi uvicorn streamlit pandas