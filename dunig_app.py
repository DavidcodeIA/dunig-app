import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import string

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Límites de productos por plan
PLANES_LIMITES = {
    "BRONCE": 3,        # Límite inicial restringido
    "PLATINUM": 15,     # Plan de $9.99
    "DIAMANTE": 50      # Plan de $29.99
}

# Función para generar código de seguridad (7 caracteres alfanuméricos)
def generar_codigo_luxury():
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choice(caracteres) for _ in range(7))

# Gestión de estados de la aplicación
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'auth_code' not in st.session_state: st.session_state.auth_code = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        animation: shimmer 5s infinite linear !important;
        color: #000 !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        border: none !important;
    }

    .luxury-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. NAVEGACIÓN Y LÓGICA DE PANELES
# ==========================================
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

# --- VISTA PÚBLICA: D'UNIG LUXURY MALL ---
if not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("🔍 Buscar tiendas exclusivas...")
        res = supabase.table("perfiles_comercio").select("*").execute()
        tiendas = [t for t in res.data if busqueda.lower() in t['nombre_comercio'].lower()]
        
        cols = st.columns(2)
        for idx, t in enumerate(tiendas):
            with cols[idx % 2]:
                st.markdown(f"<div class='luxury-card'><h3 style='text-align:center;'>{t['nombre_comercio'].upper()}</h3>", unsafe_allow_html=True)
                if st.button("VISITAR", key=f"t_{t['id']}", use_container_width=True):
                    st.session_state.tienda_actual = t
                    ir_a('tienda')
                st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        st.button("⬅️ VOLVER AL MALL", on_click=ir_a, args=('mall',))
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        for p in prods.data:
            st.video(p['video_url'])
            st.divider()

# --- VISTA RESTRINGIDA: PANEL DE CONTROL LUXURY ---
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL LUXURY</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.form("auth_form"):
            st.subheader("🔑 Acceso Propietario")
            mail = st.text_input("Email registrado")
            whatsapp = st.text_input("WhatsApp (con código de país, ej: 584120000000)")
            submit = st.form_submit_button("GENERAR CÓDIGO DE SEGURIDAD")
            
            if submit and mail and whatsapp:
                if not st.session_state.auth_code:
                    st.session_state.auth_code = generar_codigo_luxury()
                
                msj_wa = f"Tu código de acceso D'UNIG LUXURY es: *{st.session_state.auth_code}*"
                wa_url = f"https://wa.me/{whatsapp}?text={urllib.parse.quote(msj_wa)}"
                st.info("Presiona el botón para recibir tu código por WhatsApp:")
                st.link_button("📩 RECIBIR CÓDIGO", wa_url)

        st.divider()
        input_codigo = st.text_input("Introduce el código de 7 dígitos", max_chars=7).upper()
        if st.button("INGRESAR AL PANEL"):
            if input_codigo == st.session_state.auth_code:
                st.session_state.logged_in
