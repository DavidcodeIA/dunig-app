import streamlit as st
from supabase import create_client, Client

# 1. Configuración y Estética Luxury
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
    h1, h3 { color: #D4AF37 !important; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. Conexión Segura (Sin el /registros al final de la URL)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.markdown("<h1>D'UNIG PLATINUM</h1>", unsafe_allow_html=True)

# 3. Formulario (CUIDADO CON LA INDENTACIÓN AQUÍ)
with st.form("mi_formulario_luxury"):
    st.write("### ➕ Nuevo Registro")
    nombre_cliente = st.text_input("Nombre del Cliente")
    detalle_servicio = st.text_area("Información del Servicio")
    
    # EL BOTÓN DEBE ESTAR ADENTRO DEL "WITH"
    boton_enviar = st.form_submit_button("GUARDAR EN LA NUBE")

# 4. Lógica fuera del formulario (se ejecuta al presionar el botón)
if boton_enviar:
        if nombre_cliente and detalle_servicio:
            try:
                # Usamos los nombres exactos de tu SQL: NOMBRE y DETALLE
                data = {"NOMBRE": nombre_cliente, "DETALLE": detalle_servicio}
                supabase.table("registros").insert(data).execute()
                st.success("✨ ¡Gloria a Dios! Datos guardados en Supabase.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Por favor, rellena todos los campos antes de guardar.")

# 5. Visualización de datos
st.write("---")
st.write("### 📊 Registros en Tiempo Real")
try:
    response = supabase.table("registros").select("*").execute()
    if response.data:
        st.dataframe(response.data, use_container_width=True)
except:
    st.info("Crea la tabla 'registros' en Supabase para ver los datos aquí.")
