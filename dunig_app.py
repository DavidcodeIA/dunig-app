import streamlit as st
from supabase import create_client

# Conexión rápida
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.title("🧪 TEST DE CONEXIÓN RADICAL")

archivo = st.file_uploader("Sube cualquier video o foto")

if archivo:
    st.write("Intentando subir...")
    try:
        # Intento de subida forzada
        res = supabase.storage.from_("fotos_productos").upload(
            path=f"test_{archivo.name}",
            file=archivo.getvalue(),
            file_options={"content-type": "video/mp4"}
        )
        st.success("¡CONEXIÓN EXITOSA! El problema no es el permiso.")
    except Exception as e:
        st.error(f"EL ERROR REAL ES ESTE: {e}")
        st.info("Analiza el mensaje de arriba. Si dice 'Bucket not found', es que el nombre en Supabase no coincide.")
