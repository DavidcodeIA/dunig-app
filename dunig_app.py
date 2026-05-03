import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Configuración Luxury
st.set_page_config(page_title="D'UNIG Platinum v2", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #D4AF37; }
    .stButton>button { background-color: #D4AF37; color: black; border-radius: 10px; }
    h1, h3 { color: #D4AF37 !important; }
    .stDataFrame { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Conexión
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("⚜️ D'UNIG PLATINUM - Gestión de Excelencia")

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("🔍 Panel de Control")
busqueda = st.sidebar.text_input("Buscar cliente por nombre")
filtro_estado = st.sidebar.selectbox("Filtrar por estado", ["Todos", "Pendiente", "En Proceso", "Finalizado", "Cobrado"])

# --- FORMULARIO DE REGISTRO ---
with st.expander("➕ REGISTRAR NUEVO SERVICIO", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre del Cliente")
        monto = st.number_input("Monto del Servicio ($)", min_value=0.0, step=0.5)
    with col2:
        detalle = st.text_area("Descripción del Trabajo")
        estado_inicial = st.selectbox("Estado Inicial", ["Pendiente", "En Proceso", "Finalizado"])
    
    if st.button("REGISTRAR EN BASE DE DATOS"):
        if nombre and detalle:
            data = {"nombre": nombre, "detalle": detalle, "monto": monto, "estado": estado_inicial}
            supabase.table("registros").insert(data).execute()
            st.success(f"✅ ¡Gloria a Dios! Servicio de {nombre} registrado.")
            st.rerun()
        else:
            st.error("Por favor completa el nombre y el detalle.")

# --- VISUALIZACIÓN DE DATOS ---
st.write("---")
st.subheader("📊 Historial de Servicios")

try:
    # Consulta a Supabase
    query = supabase.table("registros").select("*").order("fecha", desc=True)
    response = query.execute()
    df = pd.DataFrame(response.data)

    if not df.empty:
        # Aplicar filtros
        if busqueda:
            df = df[df['nombre'].str.contains(busqueda, case=False)]
        if filtro_estado != "Todos":
            df = df[df['estado'] == filtro_estado]

        # Limpiar visualización de fecha
        df['fecha'] = pd.to_datetime(df['fecha']).dt.strftime('%d/%m/%Y %H:%M')
        
        # Mostrar tabla organizada
        st.dataframe(df[['fecha', 'nombre', 'detalle', 'monto', 'estado']], use_container_width=True)
        
        # Resumen financiero
        total_cobrado = df[df['estado'] == 'Cobrado']['monto'].sum()
        st.metric("💰 TOTAL RECAUDADO (Cobrado)", f"{total_cobrado} $")
        
    else:
        st.info("Aún no hay registros en la base de datos.")
except Exception as e:
    st.error(f"Error al cargar datos: {e}")
