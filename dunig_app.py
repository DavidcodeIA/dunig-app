import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN DE MARCA Y RENDIMIENTO
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

PLANES = {"BRONCE": 5, "PLATINUM": 15, "DIAMANTE": 50}

# --- LÓGICA DE NAVEGACIÓN ---
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None
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
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        animation: shimmer 5s infinite linear !important;
        color: #000 !important; border-radius: 30px !important; font-weight: 800;
    }
    @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
    .luxury-card {
        background: rgba(255,255,255,0.03); border: 1px solid rgba(212,175,55,0.2);
        border-radius: 20px; padding: 20px; backdrop-filter: blur(10px); margin-bottom: 20px;
    }
    footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. CUERPO DE LA APP
# ==========================================

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
        # Aquí se cargan los productos (público)
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
            whatsapp = st.text_input("WhatsApp (con código de país)")
            submit = st.form_submit_button("GENERAR CÓDIGO DE ACCESO")
            
            if submit and mail and whatsapp:
                # Generamos un código aleatorio
                codigo = str(random.randint(1000, 9999))
                st.session_state.auth_code = codigo
                # Link para "enviar" el código al usuario
                msj_wa = f"Tu código de acceso para D'UNIG LUXURY es: *{codigo}*"
                wa_url = f"https://wa.me/{whatsapp}?text={urllib.parse.quote(msj_wa)}"
                st.info("Haz clic abajo para recibir tu código por WhatsApp:")
                st.link_button("📩 RECIBIR CÓDIGO", wa_url)

        input_codigo = st.text_input("Introduce el código recibido", type="password")
        if st.button("INGRESAR AL PANEL"):
            if input_codigo == st.session_state.auth_code:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Código incorrecto")
    
    else:
        # PANEL DE CONTROL YA AUTENTICADO
        mail_auth = st.text_input("Confirmar Email para cargar datos")
        if mail_auth:
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail_auth).execute()
            if res.data:
                perf = res.data[0]
                plan = perf.get('plan', 'BRONCE').upper()
                limite = PLANES.get(plan, 5)
                
                t1, t2, t3, t4 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS", "💎 MI PLAN"])
                
                with t4:
                    st.markdown("### 🏆 Membresía Luxury")
                    col1, col2 = st.columns(2)
                    # Iconos corregidos y botones de PayPal
                    with col1:
                        st.markdown("#### 👑 Plan Platinum")
                        st.link_button("PAGAR CON PAYPAL", "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ID_PLATINUM")
                    with col2:
                        st.markdown("#### 💎 Plan Diamante")
                        st.link_button("PAGAR CON PAYPAL", "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=ID_DIAMANTE")
                    
                    st.divider()
                    st.info("Nota: Tras pagar en PayPal, reporta tu referencia en 'Reportar Pago'.")
                
                # Resto de pestañas (Agregar, Gestión, etc.) se mantienen igual...
                with t1:
                    st.write("Configuración de productos...")
            else:
                st.error("Comercio no encontrado.")
