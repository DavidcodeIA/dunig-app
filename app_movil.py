import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuración
st.set_page_config(page_title="D'UNIG - Asistente", layout="wide", page_icon="🙏")
EXCEL_FILE = 'ventas_d_unig.xlsx'

st.title("🚀 D'UNIG: Tu Guía Espiritual y Práctica")

# 1. VERIFICACIÓN DE ARCHIVO (Para saber si la app lo ve)
if os.path.exists(EXCEL_FILE):
    try:
        # Cargamos el Excel
        df = pd.read_excel(EXCEL_FILE)
        
        if df.empty:
            st.warning("⚠️ El archivo Excel está en blanco (no tiene filas).")
        else:
            st.success(f"✅ ¡Archivo detectado! Columnas encontradas: {', '.join(df.columns)}")
            
            # Mostramos los datos tal cual están en el Excel
            st.subheader("📊 Tus Datos Actuales")
            st.dataframe(df, use_container_width=True)
            
            # Intentamos crear una gráfica con las columnas que existan
            # Buscamos una columna que parezca numérica para el eje Y
            cols_numericas = df.select_dtypes(include=['number']).columns.tolist()
            if cols_numericas:
                col_y = cols_numericas[0]
                col_x = df.columns[0]
                fig = px.bar(df, x=col_x, y=col_y, title=f"Gráfico de {col_y}")
                st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
else:
    st.error(f"❌ No se encuentra el archivo '{EXCEL_FILE}' en GitHub.")
    st.info("Asegúrate de que el nombre sea minúsculas y termine en .xlsx")

st.sidebar.markdown("---")
st.sidebar.info("✨ Guardar los mandamientos de Dios y su ley como la niña de los ojos.")
