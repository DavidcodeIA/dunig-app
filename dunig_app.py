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
    layout="wide", # Wide para que el Mall ocupe toda la pantalla
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

# --- Lógica de Negocio ---
def obtener_cuentas_admin():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "cuentas_activacion").execute()
        return res.data[0]['valor'] if res.data else "⚠️ Cuentas de activación no configuradas."
    except:
        return "❌ Error al conectar con los ajustes del sistema."

PLANES_LIMITES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}
OPCIONES_PLAN_VISUAL = {
    "GRATUITO": "⚪ GRATUITO (Básico - 3 Productos)",
    "BRONCE": "🥉 BRONCE (Emprendedor - 10 Productos)",
    "PLATA": "🥈 PLATA (Crecimiento - 25 Productos)",
    "ORO": "👑 ORO (Ilimitado - Ventas Premium)"
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'registered' not in st.session_state: st.session_state.registered = False
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY & FIX DE ESPACIOS
# ==========================================
st.markdown("""
    <style>
    /* ELIMINAR ESPACIO SUPERIOR Y MARGENES LATERALES */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0rem !important;
        margin-top: -100px !important; 
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100vw !important;
    }
    
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    header, footer { visibility: hidden; }

    /* DISEÑO DIVIDIDO (MALL) */
    .tienda-split {
        height: 50vh;
        width: 100vw;
        position: relative;
        overflow: hidden;
        border-bottom: 2px solid #D4AF37;
    }
    .tienda-split img { width: 100%; height: 100%; object-fit: cover; }
    
    /* BOTONES INVISIBLES SOBRE MALL */
    div.stButton > button[key^="shop_"] {
        position: absolute; top: 0; height: 50vh !important; width: 100vw !important;
        background: transparent !important; border: none !important; color: transparent !important;
    }

    /* ESTILO FORMULARIOS Y REGISTRO */
    .welcome-card {
        background: rgba(0,0,0,0.8); padding: 30px; border-radius: 20px;
        border: 2px solid #D4AF37; text-align: center; margin: 120px 20px 20px 20px;
    }
    .stForm { margin-top: 110px !important; padding: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE PANELES (VISTAS)
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_reg = st.query_params.get("reg") == "true"

# --- PANEL 1: REGISTRO DE SOCIO ---
if es_reg:
    if st.session_state.registered:
        st.markdown(f"""
            <div class='welcome-card'>
                <h1 style='color: #D4AF37;'>💎 ¡SOLICITUD ENVIADA!</h1>
                <p>Nuestro equipo activará tu plan pronto.</p>
            </div>
            """, unsafe_allow_html=True)
        st.link_button("🚀 IR AL PANEL", "https://dunig-app-luxury-v2.streamlit.app/?admin=true", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align:center; color:#D4AF37; margin-top:110px;'>✨ REGISTRO DE SOCIO</h1>", unsafe_allow_html=True)
        with st.expander("💳 CUENTAS PARA ACTIVACIÓN"):
            st.markdown(obtener_cuentas_admin())
        
        with st.form("form_reg_externo"):
            r_nombre = st.text_input("Nombre de la Tienda")
            r_email = st.text_input("Email").lower().strip()
            r_whatsapp = st.text_input("WhatsApp")
            plan = st.selectbox("Plan", options=list(PLANES_LIMITES.keys()), format_func=lambda x: OPCIONES_PLAN_VISUAL[x])
            foto = st.file_uploader("Portada", type=['jpg', 'png'])
            pago = st.text_input("Referencia de Pago")

            if st.form_submit_button("SOLICITAR REGISTRO"):
                if r_nombre and r_email and foto:
                    st.session_state.registered = True
                    st.rerun()

# --- PANEL 2: PANEL DE CONTROL (ADMIN) ---
elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37; margin-top:110px;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    # Aquí puedes añadir la lógica de carga de productos que tenías
    st.info("Bienvenido a tu panel de gestión.")
    if st.button("SALIR"):
        st.query_params.clear()
        ir_a('mall')

# --- PANEL 3: MALL LUXURY (TIENDAS DIVIDIDAS) ---
elif st.session_state.view == 'mall':
    if supabase:
        tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).limit(2).execute().data
        for t in tiendas:
            st.markdown(f"""
                <div class="tienda-split">
                    <img src="{t.get('portada_url', '')}">
                    <div style="position:absolute; top:40%; width:100%; text-align:center;">
                        <h1 style="color:white; font-size:3rem; text-shadow:2px 2px 10px #000;">{t['nombre_comercio'].upper()}</h1>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("", key=f"shop_{t['id']}"):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA TIENDA (PRODUCTOS) ---
elif st.session_state.view == 'tienda':
    if st.button("⬅ VOLVER"): ir_a('mall')
    st.write(f"Viendo productos de: {st.session_state.tienda_actual['nombre_comercio']}")