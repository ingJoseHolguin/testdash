import streamlit as st
import sqlite3
import json
import pandas as pd

st.title("📊 Dashboard de Datos Recibidos")

# Conectar a BD
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM data")
rows = cursor.fetchall()

if rows:
    df = pd.DataFrame(rows, columns=["ID", "Payload"])
    
    # Expandir el JSON
    df["Payload"] = df["Payload"].apply(lambda x: json.loads(x))
    
    st.subheader("Datos crudos")
    st.write(df)

    st.subheader("Tabla expandida")
    try:
        expanded_df = pd.json_normalize(df["Payload"])
        st.dataframe(expanded_df)
    except Exception as e:
        st.error(f"No se pudo normalizar JSON: {e}")
else:
    st.info("Aún no hay datos en la base de datos.")
