import streamlit as st
from supabase import create_client, Client

# 1. Configuración de Estética Luxury
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

# 2. Conexión con Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.markdown("<h1>D'UNIG PLATINUM</h1>", unsafe_allow_html=True)

# 3. Formulario de Registro
with st.form("mi_formulario_luxury"):
    st.write("### ➕ Nuevo Registro")
    nombre_cliente = st.text_input("Nombre del Cliente")
    detalle_servicio = st.text_area("Información del Servicio")
    monto_pago = st.number_input("Monto (Opcional)", min_value=0.0, step=0.01)
    
    boton_enviar = st.form_submit_button("GUARDAR EN LA NUBE")

# 4. Lógica de guardado (Alineación corregida)
if boton_enviar:
    if nombre_cliente and detalle_servicio:
        try:
            # Usamos MAYÚSCULAS para que coincida con tu tabla SQL
            data = {
                "NOMBRE": nombre_cliente, 
                "DETALLE": detalle_servicio,
                "MONTO": monto_pago
            }
            supabase.table("registros").insert(data).execute()
            st.success("✨ ¡Gloria a Dios! Datos guardados exitosamente.")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
    else:
        st.warning("⚠️ Por favor, rellena los campos de Nombre y Detalle.")

# 5. Visualización de datos
st.write("---")
st.write("### 📊 Registros en Tiempo Real")
try:
    response = supabase.table("registros").select("*").execute()
    if response.data:
        st.table(response.data)
except Exception:
    st.info("Conectando con la base de datos...")
