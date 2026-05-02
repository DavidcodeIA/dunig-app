import streamlit as st
import pandas as pd
import plotly.express as px  
import os

# Configuración de la página
st.set_page_config(page_title="D'UNIG - Guía Espiritual y Práctica", layout="wide")

# Nombre del archivo de Excel
EXCEL_FILE = 'ventas_d_unig.xlsx'

st.title("🚀 D'UNIG: Tu Guía Espiritual y Práctica")

# Función para cargar datos
def cargar_datos():
    if os.path.exists(EXCEL_FILE):
        try:
            return pd.read_excel(EXCEL_FILE)
        except Exception:
            return pd.DataFrame(columns=['Fecha', 'Producto', 'Monto'])
    else:
        return pd.DataFrame(columns=['Fecha', 'Producto', 'Monto'])

# Carga de datos corregida
df_analisis = cargar_datos()

# Interfaz de la App
st.subheader("Registro de Ventas")
if not df_analisis.empty:
    st.dataframe(df_analisis)
    # Solo graficar si hay datos numéricos en 'Monto'
    try:
        fig = px.bar(df_analisis, x='Fecha', y='Monto', title="Ventas por Día")
        st.plotly_chart(fig)
    except Exception:
        st.warning("Agrega datos al Excel para ver las gráficas.")
else:
    st.info("Aún no hay datos cargados en el archivo Excel.")

st.sidebar.markdown("---")
st.sidebar.info("Guardar los mandamientos de Dios y su ley como la niña de los ojos.")
