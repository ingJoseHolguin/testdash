# dashboard.py
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import time

# --- CONFIGURACIÓN ---
DB_NAME = 'datos.db'
TABLE_NAME = 'metricas'

# --- CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT ---
st.set_page_config(
    page_title="Dashboard de Métricas en Tiempo Real",
    page_icon="📊",
    layout="wide",
)

# --- FUNCIONES ---
def cargar_datos():
    """
    Se conecta a la base de datos SQLite y carga los datos en un DataFrame de Pandas.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql(f'SELECT * FROM {TABLE_NAME}', conn)
        conn.close()
        # Convertir la columna de timestamp a formato de fecha para graficar mejor
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except:
        # Si la tabla no existe o hay un error, devuelve un DataFrame vacío
        return pd.DataFrame()

# --- LAYOUT DEL DASHBOARD ---

# Título principal
st.title("📊 Dashboard de Métricas en Tiempo Real")

# Contenedor para la actualización automática y los datos
placeholder = st.empty()

# Bucle infinito para actualizar el dashboard
while True:
    df = cargar_datos()
    
    with placeholder.container():
        # Indicador de última actualización
        st.write(f"Última actualización: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        if df.empty:
            st.warning("No hay datos en la base de datos. Envía datos al endpoint /data para verlos aquí.")
        else:
            # --- MÉTRICAS PRINCIPALES (KPIS) ---
            st.header("KPIs Principales")
            col1, col2, col3 = st.columns(3)
            
            # Usamos try-except por si las columnas no existen aún
            try:
                temp_media = df['temperatura'].mean()
                hum_media = df['humedad'].mean()
                num_registros = len(df)
                
                col1.metric("Temperatura Promedio", f"{temp_media:.2f} °C")
                col2.metric("Humedad Promedio", f"{hum_media:.2f} %")
                col3.metric("Total de Registros", f"{num_registros}")
            except KeyError:
                st.error("Las columnas 'temperatura' o 'humedad' no se encontraron en los datos.")
            
            st.divider()

            # --- GRÁFICAS ---
            st.header("Visualización de Datos")
            col_graf_1, col_graf_2 = st.columns(2)

            with col_graf_1:
                # Gráfica de evolución de la temperatura
                try:
                    fig_temp = px.line(df, x='timestamp', y='temperatura', color='user_id',
                                       title="Evolución de la Temperatura por Usuario",
                                       labels={'timestamp': 'Fecha', 'temperatura': 'Temperatura (°C)'})
                    st.plotly_chart(fig_temp, use_container_width=True)
                except (KeyError, ValueError):
                    st.info("Esperando datos con 'timestamp', 'temperatura' y 'user_id' para mostrar la gráfica.")

            with col_graf_2:
                # Gráfica de barras de humedad
                try:
                    fig_hum = px.bar(df, x='timestamp', y='humedad', color='user_id',
                                     title="Humedad Registrada por Usuario",
                                     labels={'timestamp': 'Fecha', 'humedad': 'Humedad (%)'})
                    st.plotly_chart(fig_hum, use_container_width=True)
                except (KeyError, ValueError):
                    st.info("Esperando datos con 'timestamp', 'humedad' y 'user_id' para mostrar la gráfica.")

            st.divider()

            # --- TABLA DE DATOS CRUDOS ---
            st.header("Datos Crudos")
            st.dataframe(df.tail(10)) # Muestra los últimos 10 registros

    # Espera 10 segundos antes de volver a cargar los datos
    time.sleep(10)