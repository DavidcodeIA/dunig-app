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
    layout="wide", # Cambiado a wide para que las tiendas abarquen todo el ancho
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

# --- Tus funciones de lógica ---
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
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'registered' not in st.session_state: st.session_state.registered = False
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY & FIX DE ESPACIOS (CSS)
# ==========================================
st.markdown("""
    <style>
    /* ELIMINAR ESPACIO SUPERIOR Y MARGENES LATERALES */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0rem !important;
        margin-top: -95px !important; /* Ajuste para eliminar el espacio del título */
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100vw !important;
    }
    
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    header, footer { visibility: hidden; }

    /* DISEÑO DIVIDIDO TIPO MALL (GGC3DL2GFFA7ZJVXV6LNRRRGWQ.jpg) */
    .tienda-split-container {
        height: 50vh;
        width: 100vw;
        position: relative;
        overflow: hidden;
        border-bottom: 2px solid #D4AF37;
    }

    .tienda-split-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .label-tienda {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 2.5rem;
        font-weight: 900;
        text-shadow: 2px 2px 15px #000;
        text-align: center;
        width: 100%;
        pointer-events: none;
    }

    /* BOTONES INVISIBLES SOBRE LAS IMAGENES */
    div.stButton > button[key^="shop_"] {
        position: absolute;
        top: 0;
        height: 50vh !important;
        width: 100vw !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        z-index: 10;
    }

    /* Tu estilo de botones para el formulario */
    div.stButton > button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        color: #000 !important; font-weight: 800 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS (TU CÓDIGO)
# ==========================================
es_via_register = st.query_params.get("reg") == "true"

# --- VISTA MALL (CORREGIDA PARA DIVISIÓN) ---
if st.session_state.view == 'mall' and not es_via_register:
    if supabase:
        # Traemos las tiendas activas para el Mall
        tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).limit(2).execute().data
        
        for t in tiendas:
            # HTML para la imagen dividida sin marcos
            st.markdown(f"""
                <div class="tienda-split-container">
                    <img src="{t.get('portada_url', '')}">
                    <div class="label-tienda">{t['nombre_comercio'].upper()}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Botón invisible funcional
            if st.button("", key=f"shop_{t['id']}"):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA REGISTRO (TU CÓDIGO ÍNTEGRO) ---
elif es_via_register:
    if st.session_state.registered:
        st.balloons()
        st.markdown(f"""
            <div class='welcome-card'>
                <h1 style='color: #D4AF37;'>💎 ¡BIENVENIDO A LA ÉLITE!</h1>
                <p style='font-size: 1.2rem;'>Tu solicitud ha sido recibida con éxito.</p>
                <hr style='border: 0.5px solid #D4AF37;'>
                <p>En el transcurso del día, nuestro equipo <b>activará tu plan</b>...</p>
            </div>
            """, unsafe_allow_html=True)
        st.link_button("🚀 IR AL PANEL DE CONTROL", "https://dunig-app-luxury-v2.streamlit.app/?admin=true", use_container_width=True)
    else:
        # Aquí está tu panel de registro tal cual lo pediste
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE SOCIO</h1>", unsafe_allow_html=True)
        with st.expander("💳 CUENTAS PARA ACTIVACIÓN", expanded=False):
            st.markdown(obtener_cuentas_admin())

        with st.form("form_reg_externo"):
            r_nombre_tienda = st.text_input("Nombre de la Tienda")
            r_email = st.text_input("Email del Propietario").lower().strip()
            r_whatsapp = st.text_input("WhatsApp (Ej: 58412...)")
            plan_seleccionado = st.selectbox("Selecciona tu Plan", options=list(PLANES_LIMITES.keys()), format_func=lambda x: OPCIONES_PLAN_VISUAL[x])
            r_foto_portada = st.file_uploader("Foto de Portada", type=['jpg', 'png'])
            r_referencia_pago = st.text_input("Referencia de Pago")

            if st.form_submit_button("SOLICITAR REGISTRO"):
                if r_nombre_tienda and r_email and r_whatsapp and r_foto_portada and r_referencia_pago:
                    try:
                        # Lógica de subida y guardado de tu código...
                        path_portada = f"portadas/reg_{int(time.time())}_{r_foto_portada.name}"
                        supabase.storage.from_("fotos_productos").upload(path_portada, r_foto_portada.getvalue())
                        url_portada_final = supabase.storage.from_("fotos_productos").get_public_url(path_portada)
                        
                        supabase.table("perfiles_comercio").insert({
                            "nombre_comercio": r_nombre_tienda, "email_propietario": r_email, 
                            "whatsapp": r_whatsapp, "portada_url": url_portada_final, 
                            "plan": plan_seleccionado, "referencia_pago": r_referencia_pago,
                            "codigo_acceso": f"LUX{random.randint(10,99)}", "activo": False 
                        }).execute()
                        
                        st.session_state.registered = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al registrar: {e}")