import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import uuid

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Configuración de límites de productos (Máximo 100)
PLANES_INFO = {
    "GRATUITO (Hasta 3 productos)": 3,
    "BRONCE (Hasta 10 productos)": 10,
    "PLATA (Hasta 25 productos)": 25,
    "ORO (Hasta 100 productos)": 100
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY ACTUALIZADA (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000000; color: #ffffff; }
    
    /* BOTÓN COMPRAR (PRINCIPAL) */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 55px !important; width: 100% !important; margin-bottom: 5px !important;
    }

    /* BOTÓN REGRESAR (DELGADO Y LARGO) */
    .back-bar-container button {
        background: rgba(255,255,255,0.05) !important;
        color: #ffffff !important; border: 1px solid #444 !important;
        border-radius: 8px !important; height: 35px !important;
        width: 100% !important; font-size: 0.8rem !important;
        text-transform: uppercase; letter-spacing: 1px;
    }

    /* VIDEO FULL WIDTH */
    .video-full {
        width: 100vw; position: relative; left: 50%; right: 50%;
        margin-left: -50vw; margin-right: -50vw;
        background: #000; line-height: 0;
    }
    video { width: 100% !important; height: auto !important; max-height: 80vh; object-fit: cover; }

    /* INFO BAR */
    .info-luxury-box {
        display: flex; justify-content: space-between; align-items: center;
        background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
        padding: 0 15px; height: 50px; border-radius: 12px; 
        border: 1px solid rgba(212,175,55,0.4); margin-bottom: 10px;
    }
    .p-title { color: #D4AF37; font-weight: 700; text-transform: uppercase; font-size: 0.9rem; }
    .p-price { color: #39FF14; font-weight: 900; font-size: 1.1rem; }

    .img-cuadrada { width: 100%; aspect-ratio: 1/1; object-fit: cover; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================

# --- REGISTRO DE SOCIO CON BENEFICIOS ---
if st.query_params.get("reg") == "true":
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO SOCIO</h1>", unsafe_allow_html=True)
    with st.form("reg_form"):
        n = st.text_input("Nombre de la Tienda")
        e = st.text_input("Email de Propietario")
        w = st.text_input("WhatsApp (Formato: 58412...)")
        
        # Menú desplegable con beneficios detallados
        plan_seleccionado = st.selectbox("Selecciona tu Plan de Expansión", list(PLANES_INFO.keys()))
        
        img = st.file_uploader("Subir Imagen de Portada (1:1 recomendado)", type=['jpg', 'png'])
        ref = st.text_input("Referencia de Pago")
        
        if st.form_submit_button("SOLICITAR ACTIVACIÓN"):
            if n and e and w and img:
                # Lógica de guardado...
                st.success(f"¡Solicitud enviada! Plan seleccionado: {plan_seleccionado}")
                ir_a('mall')

# --- VISTA: MALL ---
elif st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    cols = st.columns(2)
    for i, t in enumerate(tiendas):
        with cols[i % 2]:
            st.markdown(f'<img src="{t["portada_url"]}" class="img-cuadrada">', unsafe_allow_html=True)
            if st.button(f"ENTRAR {t['nombre_comercio'].upper()}", key=f"t_{t['id']}"):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA: TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        # Video Full Width
        st.markdown('<div class="video-full">', unsafe_allow_html=True)
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Barra de Info (Nombre + Precio)
        st.markdown(f"""
            <div class="info-luxury-box">
                <span class="p-title">{p['nombre_producto']}</span>
                <span class="p-price">${p['precio']}</span>
            </div>
        """, unsafe_allow_html=True)

        # Botón Comprar (Principal)
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            # Aquí abre tu diálogo de pago
            pass
        
        # Botón Regresar (Delgado, largo y debajo del de comprar)
        st.markdown('<div class="back-bar-container">', unsafe_allow_html=True)
        if st.button("⬅ REGRESAR AL MALL", key=f"back_{p['id']}", use_container_width=True):
            ir_a('mall')
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()