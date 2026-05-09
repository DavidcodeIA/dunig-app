import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import time

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

@st.cache_resource 
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

supabase = init_connection()

# --- Lógica de negocio restaurada ---
PLANES_LIMITES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}
OPCIONES_PLAN_VISUAL = {
    "GRATUITO": "⚪ GRATUITO (Básico - 3 Productos)",
    "BRONCE": "🥉 BRONCE (Emprendedor - 10 Productos)",
    "PLATA": "🥈 PLATA (Crecimiento - 25 Productos)",
    "ORO": "👑 ORO (Ilimitado - Ventas Premium)"
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY & FIX TOTAL (CSS)
# ==========================================
st.markdown("""
    <style>
    /* ELIMINAR ESPACIO SUPERIOR Y MARGENES LATERALES */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0rem !important;
        margin-top: -105px !important; 
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100vw !important;
    }
    
    .main { background: #000; color: #ffffff; }
    header, footer { visibility: hidden; }

    /* DISEÑO DIVIDIDO (MALL) */
    .tienda-split {
        height: 50vh;
        width: 100vw;
        position: relative;
        overflow: hidden;
    }

    .tienda-split img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* PANEL DE CONTROL (CONTENEDOR) */
    .admin-card {
        background: rgba(20, 20, 20, 0.9);
        border: 1px solid #D4AF37;
        padding: 20px;
        border-radius: 15px;
        margin: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. GESTOR DE VISTAS (PANELES)
# ==========================================

# A. DETECTAR SI ES ADMIN (PANEL DE CONTROL)
es_admin = st.query_params.get("admin") == "true"

if es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37; margin-top:110px;'>💎 PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    
    # Aquí va la lógica de tu panel que ya tenías
    with st.container():
        st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Ventas Hoy", "$ 0.00")
        with col2:
            st.metric("Productos Activos", "0")
        
        # Formulario de carga de productos o gestión
        st.subheader("Gestión de Inventario")
        # ... (Tu código de gestión de productos aquí) ...
        
        if st.button("SALIR DEL PANEL"):
            st.query_params.clear()
            ir_a('mall')
        st.markdown("</div>", unsafe_allow_html=True)

# B. VISTA REGISTRO (VÍA URL)
elif st.query_params.get("reg") == "true":
    st.markdown("<h1 style='text-align:center; color:#D4AF37; margin-top:110px;'>✨ REGISTRO DE SOCIO</h1>", unsafe_allow_html=True)
    # ... (Tu formulario de registro íntegro) ...
    with st.form("registro_socio"):
        st.text_input("Nombre de la Tienda")
        if st.form_submit_button("SOLICITAR"):
            st.success("Solicitud enviada")

# C. VISTA MALL (PANTALLA DIVIDIDA)
elif st.session_state.view == 'mall':
    if supabase:
        tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).limit(2).execute().data
        for t in tiendas:
            st.markdown(f"""
                <div class="tienda-split">
                    <img src="{t.get('portada_url', '')}">
                    <div style="position:absolute; top:40%; width:100%; text-align:center;">
                        <h1 style="color:white; font-size:3rem; text-shadow:2px 2px 10px #000;">{t['nombre_comercio']}</h1>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("ENTRAR", key=f"btn_{t['id']}", use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')
    
    # Acceso rápido al panel si estás en desarrollo
    st.write("")
    if st.button("⚙️"):
        st.query_params["admin"] = "true"
        st.rerun()

# D. VISTA TIENDA (TIKTOK STYLE)
elif st.session_state.view == 'tienda':
    if st.button("⬅ VOLVER AL MALL"): ir_a('mall')
    # ... (Tu lógica de videos TikTok) ...