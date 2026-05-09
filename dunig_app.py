import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import time
from datetime import datetime, date

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="wide", # Cambiado a wide para que el Mall ocupe toda la pantalla
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

# --- LÓGICA DE NEGOCIO INTEGRADA (TU LÓGICA ORIGINAL) ---
def verificar_expiracion(perfil):
    if perfil.get('plan') == "GRATUITO":
        try:
            f_reg_raw = perfil.get('fecha_registro')
            fecha_reg = datetime.strptime(str(f_reg_raw), '%Y-%m-%d').date() if f_reg_raw else date.today()
            dias_transcurridos = (date.today() - fecha_reg).days
            if dias_transcurridos >= 7 and perfil.get('activo') == True:
                supabase.table("perfiles_comercio").update({"activo": False}).eq("id", perfil['id']).execute()
                return False
        except:
            return perfil.get('activo', False)
    return perfil.get('activo', False)

PLANES_LIMITES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}
OPCIONES_PLAN_VISUAL = {
    "GRATUITO": "⚪ GRATUITO (Prueba 7 Días - 3 Productos)",
    "BRONCE": "🥉 BRONCE (Emprendedor - 10 Productos)",
    "PLATA": "🥈 PLATA (Crecimiento - 25 Productos)",
    "ORO": "👑 ORO (Ilimitado - Ventas Premium)"
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'registered' not in st.session_state: st.session_state.registered = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS MEJORADO)
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
    
    .main { background: #000; color: #ffffff; }
    header, footer { visibility: hidden; }

    /* DISEÑO MALL DIVIDIDO */
    .split-container {
        height: 50vh;
        width: 100vw;
        position: relative;
        overflow: hidden;
        border-bottom: 2px solid #D4AF37;
    }
    .split-container img { width: 100%; height: 100%; object-fit: cover; }
    
    /* BOTÓN INVISIBLE SOBRE LA TIENDA */
    div.stButton > button[key^="btn_"] {
        position: absolute; top: 0; height: 50vh !important; width: 100vw !important;
        background: transparent !important; border: none !important; color: transparent !important;
        z-index: 10;
    }

    /* ESTILO FORMULARIOS (Para que no queden pegados arriba) */
    .form-spacing { margin-top: 120px; padding: 20px; }
    
    .welcome-card {
        background: rgba(0,0,0,0.8); padding: 40px; border-radius: 25px;
        border: 2px solid #D4AF37; text-align: center; margin: 120px 20px 20px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS (PANELES)
# ==========================================
es_admin_master = st.query_params.get("admin") == "true"
es_via_register = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO ---
if es_via_register:
    if st.session_state.registered:
        st.markdown("<div class='welcome-card'><h1>BIENVENIDO SOCIO</h1><p>Solicitud procesada.</p></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='form-spacing'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO LUXURY</h1>", unsafe_allow_html=True)
        with st.form("form_reg_clean"):
            r_nombre = st.text_input("Nombre de la Tienda")
            r_email = st.text_input("Email").lower().strip()
            r_whatsapp = st.text_input("WhatsApp")
            r_plan = st.selectbox("Plan", options=list(PLANES_LIMITES.keys()), format_func=lambda x: OPCIONES_PLAN_VISUAL[x])
            r_foto = st.file_uploader("Portada", type=['jpg', 'png'])
            r_ref = st.text_input("Referencia de Pago")
            
            if st.form_submit_button("REGISTRAR"):
                # Aquí va tu lógica de insert que ya funciona
                st.session_state.registered = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- VISTA: MALL (DISEÑO DIVIDIDO) ---
elif not es_admin_master:
    if st.session_state.view == 'mall':
        datos_tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).limit(2).execute().data
        tiendas = [t for t in datos_tiendas if verificar_expiracion(t)]
        
        if not tiendas:
            st.markdown("<div class='welcome-card'>Próximamente más aperturas...</div>", unsafe_allow_html=True)
        else:
            for t in tiendas:
                st.markdown(f"""
                    <div class="split-container">
                        <img src="{t.get('portada_url', '')}">
                        <div style="position:absolute; top:40%; width:100%; text-align:center;">
                            <h1 style="color:white; font-size:3rem; text-shadow:2px 2px 15px #000;">{t['nombre_comercio'].upper()}</h1>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("", key=f"btn_{t['id']}"):
                    st.session_state.tienda_actual = t
                    ir_a('tienda')

# --- VISTA: PANEL SOCIO ---
else:
    st.markdown("<div class='form-spacing'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE SOCIO</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.form("login"):
            l_email = st.text_input("Email").strip().lower()
            l_code = st.text_input("Código", type="password")
            if st.form_submit_button("INGRESAR"):
                # Tu lógica de login que ya funciona
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.success(f"Sesión activa: {st.session_state.user_email}")
        if st.button("SALIR"):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)