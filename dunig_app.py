import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

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

PLANES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY Y LOGOS CUADRADOS (CSS)
# ==========================================
st.markdown("""
    <style>
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .stApp { background-color: #000; color: white; }
    header, footer { visibility: hidden; }

    /* LOGOS EN EL MALL: Pantalla cuadrada completa */
    .img-cuadrada {
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        border: 2px solid #D4AF37;
        margin-bottom: 10px;
        display: block;
    }

    /* TIENDA: Video Full Screen */
    .video-canvas { position: relative; width: 100vw; height: 100vh; overflow: hidden; }
    .stVideo { position: absolute; top: 0; left: 0; width: 100vw !important; height: 100vh !important; }
    .stVideo video { object-fit: cover !important; width: 100vw !important; height: 100vh !important; }

    /* UI SOBRE EL VIDEO */
    .ui-overlay {
        position: absolute; bottom: 50px; left: 20px; z-index: 999;
        display: flex; flex-direction: column; gap: 15px; pointer-events: none;
    }
    .ui-overlay button, .ui-overlay .price-bubble-float { pointer-events: auto !important; }

    .stButton > button {
        background: transparent !important; border: none !important; padding: 0 !important;
        font-size: 60px !important; color: white !important; text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
    }

    .price-bubble-float {
        background: #FFD700; color: black; padding: 5px 20px; border-radius: 50px;
        font-weight: 900; font-size: 2.2rem; display: inline-block; border: 2px solid #000;
    }

    .luxury-text {
        color: #1E4D92; font-weight: 900; text-transform: uppercase;
        -webkit-text-stroke: 1.5px white; margin: 0; line-height: 1;
    }
    .brand-title { font-size: 2.5rem; }
    .product-title { font-size: 3rem; margin-top: -5px; }
    </style>
    """, unsafe_allow_html