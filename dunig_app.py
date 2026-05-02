import streamlit as st
from supabase import create_client, Client

# 1. Configuración de Estilo Luxury
st.set_page_config(page_title="D'UNIG Luxury", layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #D4AF37; }
    header, footer, #MainMenu {visibility: hidden;}
    .stButton>button {
        background-color: #D4AF37; color: black;
        border-radius: 15px; font-weight: bold; width: 100%;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Conexión con Supabase (usando los Secrets que pegaste en Streamlit)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.markdown("<h1>D'UNIG PLATINUM</h1>", unsafe_allow_html=True)

# 3. Formulario para agregar información
with st.form("registro_luxury"):
    st.write("### ➕ Nuevo Registro")
    nombre = st.text_input("Nombre del Cliente")
    detalle = st.text_area("Información del Servicio")
    
if st.form_submit_button("GUARDAR EN LA NUBE"):
        try:
            data = {"nombre": nombre, "detalle": detalle}
            # Intentamos guardar
            supabase.table("registros").insert(data).execute()
            st.success("✨ ¡Registro guardado exitosamente en D'UNIG Platinum!")
        except Exception as e:
            st.error(f"Error de conexión: {e}")
            st.info("Revisa si desactivaste el RLS en Supabase o si la URL es correcta.")
# 4. Mostrar los datos guardados
st.write("---")
st.write("### 📊 Registros Actuales")
try:
    response = supabase.table("registros").select("*").execute()
    if response.data:
        st.table(response.data)
except Exception as e:
    st.error("Asegúrate de haber creado la tabla 'registros' en Supabase.")
