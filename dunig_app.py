import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA
# ==========================================
# Forzamos que el sidebar esté expandido al iniciar
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="centered", 
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS MAESTRO: MARCA BLANCA + SIDEBAR FIJO
# ==========================================
st.markdown("""
    <style>
    /* 1. OCULTAR LOGO Y PUBLICIDAD INFERIOR */
    footer {visibility: hidden;}
    
    /* 2. OCULTAR BOTÓN DE 'MANAGE APP' Y MENÚ DE STREAMLIT (DERECHA) */
    #MainMenu {visibility: hidden;}
    
    /* 3. ¡IMPORTANTE! MANTENER EL BOTÓN DEL SIDEBAR (IZQUIERDA) */
    /* No ocultamos el 'header' completo, solo los elementos de la derecha */
    header[data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }
    
    /* Ocultamos específicamente el botón de opciones de la derecha pero dejamos el de la izquierda */
    header[data-testid="stHeader"] > div:nth-child(1) > div:nth-child(2) {
        display: none;
    }

    /* 4. ESTÉTICA LUXURY */
    .main { background-color: #000000; color: #ffffff; }
    
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 2px solid #D4AF37;
        z-index: 1000;
    }
    
    /* Personalización de botones en el Sidebar */
    [data-testid="stSidebar"] .stButton>button {
        background: #D4AF37 !important;
        color: black !important;
        font-weight: bold;
        border: none;
        width: 100%;
    }

    .price-bubble {
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(0, 0, 0, 0.8);
        color: #39FF14; 
        padding: 8px 20px;
        border-radius: 30px;
        font-weight: 900;
        border: 2px solid #39FF14;
        z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. EL PANEL LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>D'UNIG</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; margin-top:-20px; color:white;'>LUXURY EDITION</p>", unsafe_allow_html=True)
    st.divider()
    
    # Botones Claros para Navegar
    if st.button("🏠 IR AL MALL"):
        ir_a('mall')
        
    if st.button("⚙️ PANEL CONTROL"):
        ir_a('admin')
        
    st.markdown("<br><br>"*10, unsafe_allow_html=True) # Espacio
    st.caption("© 2026 D'UNIG LUXURY")

# ==========================================
# 4. LÓGICA DE VISTAS (RESUMIDA)
# ==========================================

if st.session_state.view == 'mall':
    st.title("🏙️ LUXURY MALL")
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    cols = st.columns(2)
    for idx, t in enumerate(tiendas.data):
        with cols[idx % 2]:
            if st.button(f"✨ {t['nombre_comercio'].upper()}", key=f"m_{t['id']}"):
                st.session_state.tienda_actual = t
                ir_a('tienda')

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if st.button("⬅️ VOLVER"): ir_a('mall')
    st.title(f"✨ {t['nombre_comercio']}")
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    for p in prods.data:
        st.markdown(f'<div style="position: relative;"><div class="price-bubble">${p["precio"]}</div></div>', unsafe_allow_html=True)
        st.video(p['video_url'])
        st.markdown(f"**{p['nombre_producto']}**")
        st.divider()

elif st.session_state.view == 'admin':
    st.title("🚀 ADMIN LUXURY")
    mail = st.text_input("Email de Propietario")
    if mail:
        st.success(f"Bienvenido. Gestiona tus productos aquí.")
        # Aquí va el resto de tu lógica de agregar/borrar productos...
