import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA LUXURY ---
st.set_page_config(page_title="D'UNIG PLATINUM - Delivery & Gestión", layout="wide")

# --- ESTÉTICA PROFESIONAL SIN PUBLICIDAD ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #0E1117; color: #D4AF37; }
    .stButton>button { 
        background-color: #D4AF37; 
        color: black; 
        border-radius: 10px; 
        font-weight: bold;
        width: 100%;
    }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    .stDataFrame { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A BASE DE DATOS ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- TÍTULO PRINCIPAL ---
st.title("⚜️ D'UNIG PLATINUM")
st.write("---")

# --- MENÚ DE NAVEGACIÓN ---
opcion = st.sidebar.selectbox("Selecciona un Módulo", 
    ["📦 Inventario Delivery", "🛠️ Registro de Servicios", "📊 Reportes de Ventas"])

# ==========================================
# MÓDULO 1: INVENTARIO DELIVERY (PARA COMERCIOS)
# ==========================================
if opcion == "📦 Inventario Delivery":
    st.header("Gestionar Vitrina de Productos")
    
    with st.expander("➕ Cargar Nuevo Producto", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre_prod = st.text_input("Nombre del Producto")
            precio_prod = st.number_input("Precio de Venta ($)", min_value=0.0, step=0.01)
            categoria_prod = st.selectbox("Categoría", ["Comida", "Bebidas", "Ropa", "Electrónica", "Otros"])
        with col2:
            stock_prod = st.number_input("Cantidad en Inventario", min_value=0, step=1)
            url_foto = st.text_input("URL de la Imagen (Link)")
            nombre_negocio = st.text_input("Nombre del Comercio")

        if st.button("AÑADIR PRODUCTO A VITRINA"):
            if nombre_prod and precio_prod > 0:
                data_prod = {
                    "nombre_producto": nombre_prod,
                    "precio": precio_prod,
                    "stock": stock_prod,
                    "categoria": categoria_prod,
                    "imagen_url": url_foto,
                    "comercio_nombre": nombre_negocio
                }
                try:
                    supabase.table("productos").insert(data_prod).execute()
                    st.success(f"✅ ¡Gloria a Dios! {nombre_prod} ya está en la vitrina.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar producto: {e}")
            else:
                st.warning("Por favor rellena los campos obligatorios (Nombre y Precio).")

    # Mostrar Vitrina actual
    st.subheader("🖼️ Vista de la Vitrina")
    try:
        res = supabase.table("productos").select("*").execute()
        df_prod = pd.DataFrame(res.data)
        if not df_prod.empty:
            st.dataframe(df_prod[['nombre_producto', 'precio', 'stock', 'categoria', 'comercio_nombre']], use_container_width=True)
        else:
            st.info("La vitrina está vacía.")
    except:
        st.info("Aún no hay productos registrados.")

# ==========================================
# MÓDULO 2: REGISTRO DE SERVICIOS (CONTROL INTERNO)
# ==========================================
elif opcion == "🛠️ Registro de Servicios":
    st.header("Control de Servicios y Clientes")
    
    with st.expander("📝 Nuevo Registro de Servicio"):
        c1, c2 = st.columns(2)
        with c1:
            nombre_cliente = st.text_input("Nombre del Cliente")
            monto_serv = st.number_input("Monto ($)", min_value=0.0)
        with c2:
            detalle_serv = st.text_area("Detalle del Trabajo")
            estado_serv = st.selectbox("Estado", ["Pendiente", "En Proceso", "Finalizado", "Cobrado"])
        
        if st.button("GUARDAR SERVICIO"):
            if nombre_cliente and detalle_serv:
                data_serv = {
                    "nombre": nombre_cliente,
                    "detalle": detalle_serv,
                    "monto": monto_serv,
                    "estado": estado_serv
                }
                supabase.table("registros").insert(data_serv).execute()
                st.success("✅ Registro guardado exitosamente.")
                st.rerun()

    # Historial de servicios
    try:
        res_serv = supabase.table("registros").select("*").order("fecha", desc=True).execute()
        df_serv = pd.DataFrame(res_serv.data)
        if not df_serv.empty:
            st.dataframe(df_serv[['fecha', 'nombre', 'detalle', 'monto', 'estado']], use_container_width=True)
    except:
        st.info("No hay servicios registrados aún.")

# ==========================================
# MÓDULO 3: REPORTES DE VENTAS
# ==========================================
else:
    st.header("📊 Resumen Financiero")
    try:
        res_reg = supabase.table("registros").select("monto", "estado").execute()
        df_reg = pd.DataFrame(res_reg.data)
        
        if not df_reg.empty:
            total_cobrado = df_reg[df_reg['estado'] == 'Cobrado']['monto'].sum()
            st.metric("💰 TOTAL COBRADO (Servicios)", f"{total_cobrado} $")
            
            # Gráfico simple
            st.bar_chart(df_reg.groupby('estado')['monto'].sum())
        else:
            st.write("No hay datos suficientes para reportes.")
    except:
        st.error("Error al cargar reportes.")
