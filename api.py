# api.py
import sqlite3
import pandas as pd
from fastapi import FastAPI, Request
from sqlalchemy import create_engine

# --- CONFIGURACIÓN ---
DB_NAME = 'datos.db'
TABLE_NAME = 'metricas'

# Creamos el motor de SQLAlchemy para que Pandas pueda comunicarse con la DB
# El 'check_same_thread' es importante para que SQLite funcione bien con FastAPI
engine = create_engine(f'sqlite:///{DB_NAME}?check_same_thread=False')

# Creamos la aplicación FastAPI
app = FastAPI(
    title="API de Captura de Datos",
    description="Un endpoint simple para recibir datos JSON y guardarlos en SQLite."
)

@app.on_event("startup")
def startup_event():
    """
    Función que se ejecuta al iniciar la API.
    Verifica si la tabla existe y, si no, la crea.
    """
    print("Iniciando API y preparando base de datos...")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Una consulta simple para crear la tabla si no existe.
        # Se asume un JSON con 'timestamp', 'temperatura', 'humedad' y 'user_id'.
        # Puedes ajustar las columnas según el JSON que esperas recibir.
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            temperatura REAL,
            humedad REAL,
            user_id TEXT
        );
        """)
        conn.commit()
        conn.close()
        print("Base de datos y tabla listas.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")


@app.post("/data")
async def recibir_datos(request: Request):
    """
    Endpoint para recibir un JSON vía POST y guardarlo en la base de datos.
    """
    try:
        # Obtiene el JSON del cuerpo de la petición
        datos_json = await request.json()
        print(f"Datos recibidos: {datos_json}")

        # Convierte el JSON a un DataFrame de Pandas
        # Usamos una lista para que el DataFrame tenga la estructura correcta
        df = pd.DataFrame([datos_json])

        # Guarda el DataFrame en la base de datos SQLite
        # 'append' añade los datos si la tabla ya existe.
        # 'index=False' para no guardar el índice del DataFrame en la tabla.
        df.to_sql(TABLE_NAME, engine, if_exists='append', index=False)

        return {"status": "ok", "message": "Datos guardados correctamente"}

    except Exception as e:
        print(f"Error al procesar la petición: {e}")
        return {"status": "error", "message": str(e)}

# Para ejecutar:
# En la terminal, dentro de la carpeta de tu proyecto, usa el comando:
# uvicorn api:app --reload