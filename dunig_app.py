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
    layout="centered", 
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

# --- TU LÓGICA DE NEGOCIO (EXPIRACIÓN) ---
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
# 2. ESTÉTICA LUXURY (SIN 50-50, BOTONES CON TÍTULO)
# ==========================================
st.markdown("""
    <style>
    /* ELIMINAR ESPACIO SUPERIOR */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 1rem !important;
        margin-top: -30px !important; 
    }
    
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    header, footer { visibility: hidden; }

    /* ESTILO DE BOTÓN DORADO */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 15px !important;
        font-weight: 800 !important; border: none !important;
        width: 100% !important;
    }

    /* IMAGEN DE TIENDA COMO ESTABA ANTES */
    .img-mall-luxury {
        width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 20px;
        border: 1px solid #D4AF37; margin-bottom: 10px;
    }

    .form-container { padding: 20px; margin-top: 50px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================
es_admin_master = st.query_params.get("admin") == "true"
es_via_register = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO ---
if es_via_register:
    if st.session_state.registered:
        st.success("SOLICITUD ENVIADA")
    else:
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO LUXURY</h1>", unsafe_allow_html=True)
        with st.form("form_reg_clean"):
            r_nombre = st.text_input("Nombre de la Tienda")
            r_email = st.text_input("Email").lower().strip()
            r_whatsapp = st.text_input("WhatsApp")
            r_plan = st.selectbox("Plan", options=list(PLANES_LIMITES.keys()), format_func=lambda x: OPCIONES_PLAN_VISUAL[x])
            r_foto = st.file_uploader("Portada", type=['jpg', 'png'])
            r_ref = st.text_input("Referencia de Pago")
            
            if st.form_submit_button("REGISTRAR MI COMERCIO"):
                # Tu lógica de registro original aquí
                st.session_state.registered = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- VISTA: MALL (DISEÑO ORIGINAL DE CUADRÍCULA) ---
elif not es_admin_master:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        datos_tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
        tiendas = [t for t in datos_tiendas if verificar_expiracion(t)]
        
        if not tiendas:
            st.info("Próximamente más aperturas...")
        else:
            # Volvemos a las 2 columnas clásicas
            for i in range(0, len(tiendas), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(tiendas):
                        t = tiendas[i + j]
                        with cols[j]:
                            st.markdown(f'<img src="{t.get("portada_url", "")}" class="img-mall-luxury">', unsafe_allow_html=True)
                            # Botón con el nombre de la tienda como título de ingreso
                            if st.button(f"INGRESAR A {t['nombre_comercio'].upper()}", key=f"btn_{t['id']}"):
                                st.session_state.tienda_actual = t
                                ir_a('tienda')

# --- VISTA: PANEL SOCIO ---
else:
    st.markdown("<div class='form-container'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE SOCIO</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.form("login"):
            l_email = st.text_input("Email").strip().lower()
            l_code = st.text_input("Código", type="password")
            if st.form_submit_button("INGRESAR AL PANEL"):
                # Tu lógica de login original aquí
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.success(f"Sesión activa: {st.session_state.user_email}")
        if st.button("SALIR"):
            st.session_state.logged_in = False
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)