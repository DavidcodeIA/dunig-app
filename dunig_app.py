import streamlit as st
from supabase import create_client

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Capturar parámetros de la URL para que los enlaces funcionen
query_params = st.query_params

# Lógica de navegación basada en la URL o el estado de sesión
if "admin" in query_params and query_params["admin"] == "true":
    st.session_state.view = 'admin_panel'
elif "reg" in query_params and query_params["reg"] == "true":
    st.session_state.view = 'registro_socio'
elif 'view' not in st.session_state:
    st.session_state.view = 'mall'

if 'tienda_actual' not in st.session_state:
    st.session_state.tienda_actual = None

@st.cache_resource 
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        return None

supabase = init_connection()

def ir_a(pagina):
    # Al navegar manualmente, limpiamos los parámetros de la URL para evitar bucles
    st.query_params.clear()
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS INTEGRAL (SIN BARRAS Y DE LUJO)
# ==========================================
st.markdown("""
    <style>
    header, footer, [data-testid="stSidebar"] { visibility: hidden; display: none !important; }
    
    html, body, .main, [data-testid="stAppViewBlockContainer"] {
        overflow: hidden !important;
        margin: 0 !important; padding: 0 !important;
        width: 100vw !important; height: 100vh !important;
        background-color: #000 !important;
    }

    [data-testid="stAppViewBlockContainer"] { margin-top: -100px !important; }

    /* Estilo para los Paneles Administrativos */
    .admin-scroll-container {
        background: #0a0a0a;
        height: 100vh;
        padding: 50px 25px;
        color: white;
        overflow-y: auto !important; /* Aquí sí permitimos scroll para formularios */
    }

    /* Botones de navegación */
    div.stButton > button[key^="back_"] {
        position: fixed; top: 30px; left: 20px; z-index: 2000;
        background: rgba(0,0,0,0.8) !important; color: #D4AF37 !important;
        border: 1px solid #D4AF37 !important; border-radius: 50px !important;
    }
    
    /* Inputs Estilizados */
    input, select, textarea {
        background-color: #1a1a1a !important;
        color: #D4AF37 !important;
        border: 1px solid #333 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS (PANELES REACTIVADOS)
# ==========================================

# --- VISTA: REGISTRO DE SOCIOS (?reg=true) ---
if st.session_state.view == 'registro_socio':
    st.markdown('<div class="admin-scroll-container">', unsafe_allow_html=True)
    if st.button("⬅ VOLVER AL MALL", key="back_reg"): ir_a('mall')
    
    st.title("📝 Registro de Nuevo Socio")
    st.write("Bienvenido a la red de exclusividad D'UNIG.")
    
    with st.form("form_registro"):
        col1, col2 = st.columns(2)
        with col1:
            nombre_comercio = st.text_input("Nombre del Comercio")
            email = st.text_input("Correo Electrónico")
        with col2:
            propietario = st.text_input("Nombre del Propietario")
            telefono = st.text_input("WhatsApp de contacto")
            
        plan = st.selectbox("Selecciona tu Plan", ["Básico", "Premium", "Luxury VIP"])
        portada_url = st.text_input("URL de Imagen de Portada para el Mall")
        
        if st.form_submit_button("SOLICITAR REGISTRO"):
            st.success("Solicitud enviada. Revisaremos tus datos pronto.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- VISTA: PANEL ADMINISTRATIVO (?admin=true) ---
elif st.session_state.view == 'admin_panel':
    st.markdown('<div class="admin-scroll-container">', unsafe_allow_html=True)
    if st.button("⬅ SALIR DEL PANEL", key="back_admin"): ir_a('mall')
    
    st.title("📊 Panel de Control D'UNIG")
    
    # Aquí puedes agregar la lógica de gestión que tenías antes
    if supabase:
        st.subheader("Estadísticas Rápidas")
        col1, col2, col3 = st.columns(3)
        col1.metric("Comercios", "12")
        col2.metric("Productos", "45")
        col3.metric("Visitas hoy", "+1.2k")
        
        st.write("### Listado de Comercios")
        comercios = supabase.table("perfiles_comercio").select("*").execute().data
        st.dataframe(comercios)
    st.markdown('</div>', unsafe_allow_html=True)

# --- VISTA: MALL (Pantalla Principal) ---
elif st.session_state.view == 'mall':
    # [Aquí va tu código de pantalla dividida con imágenes]
    if supabase:
        tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).limit(2).execute().data
        for idx, t in enumerate(tiendas):
            st.markdown(f'<div class="shop-half" style="height:50vh; position:relative; overflow:hidden;"><img src="{t.get("portada_url", "")}" style="width:100%; height:100%; object-fit:cover;"><div class="shop-label" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); color:white; font-size:2rem; font-weight:900; text-shadow:2px 2px 10px #000;">{t["nombre_comercio"]}</div></div>', unsafe_allow_html=True)
            if st.button(f"Entrar {idx}", key=f"link_{t['id']}", help="Entrar a tienda", use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA: TIENDA (Videos TikTok) ---
elif st.session_state.view == 'tienda':
    # [Aquí va tu código de videos edge-to-edge con Audio Focus]
    pass