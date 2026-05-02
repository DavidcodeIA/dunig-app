import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configuración de la página
st.set_page_config(page_title="D'UNIG - Guía Digital", layout="wide")

st.title("D'UNIG: Tu Asistente en la Nube")

# Conexión con Google Drive (ya configurada en Secrets)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    
    st.success("¡Datos cargados correctamente desde Google Drive!")
    st.dataframe(df)
    
except Exception as e:
    st.error(f"Error al conectar con Google: {e}")
    st.info("Revisa que el link en Secrets sea el correcto.")

st.sidebar.markdown("---")
st.sidebar.info("Guardar los mandamientos de Dios y su ley como la niña de los ojos.")
