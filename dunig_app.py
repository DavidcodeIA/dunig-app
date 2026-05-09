import streamlit as st
from supabase import create_client
import urllib.parse

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

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA "AUDIO FOCUS" & FULL UI (CSS)
# ==========================================
st.markdown("""
    <style>
    /* ELIMINACIÓN TOTAL DE MÁRGENES (FIX PARA SCREENSHOT) */
    .main { background-color: #000000 !important; }
    header { visibility: hidden; height: 0px !important; } 
    footer { visibility: hidden; }
    
    [data-testid="stAppViewBlockContainer"] {
        padding: 0rem !important;
        margin: 0rem !important;
    }

    /* Scroll Snapping para control de Audio Activo */
    [data-testid="stVerticalBlock"] {
        scroll-snap-type: y mandatory;
        overflow-y: scroll;
        height: 100vh;
        gap: 0rem !important;
    }

    .snap-section {
        scroll-snap-align: start;
        scroll-snap-stop: always;
        position: relative;
        width: 100vw;
        height: 100vh;
        background: #000;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Botón ATRÁS (Burbuja Naranja - Visible Arriba) */
    div.stButton > button[key^="back_"] {
        position: fixed;
        top: 10px !important; 
        left: 10px !important;
        z-index: 1000 !important;
        background: rgba(0, 0, 0, 0.7) !important;
        color: #FF5F1F !important; 
        border: 2px solid #FF5F1F !important;
        border-radius: 50px !important;
        font-weight: 900 !important;
        height: 45px !important;
        padding: 0px 20px !important;
    }

    /* Botón COMPRAR (Dorado - Fijo en Base) */
    div.stButton > button[key^="buy_"] {
        position: fixed;
        bottom: 0px !important;
        left: 0px !important;
        z-index: 999 !important;
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        color: #000 !important; 
        border-radius: 0px !important; 
        font-weight: 900 !important;
        height: 70px !important;
        border: none !important;
        width: 100% !important;
        font-size: 1.4rem !important;
    }

    .floating-info {
        position: absolute;
        bottom: 90px;
        left: 20px;
        z-index: 100;
        color: white;
        text-shadow: 2px 2px 5px #000;
        pointer-events: none;
    }

    ::-webkit-scrollbar { display: none; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE TIENDA E INTERFAZ
# ==========================================
if st.session_state.view == 'mall':
    tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(tiendas):
                t = tiendas[i + j]
                with cols[j]:
                    st.image(t.get("portada_url", ""), use_container_width=True)
                    if st.button(f"{t['nombre_comercio'].upper()}", key=f"t_{t['id']}", use_container_width=True):
                        st.session_state.tienda_actual = t
                        ir_a('tienda')

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    # Botón Atrás Maestro
    if st.button("⬅ ATRÁS", key="back_master"):
        ir_a('mall')

    for idx, p in enumerate(prods):
        # Reproducción con Audio Focus simulado: Autoplay sin mute
        st.markdown(f"""
            <div class="snap-section">
                <video class="tiktok-video" autoplay loop playsinline>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                <div class="floating-info">
                    <div style="font-size: 1.8rem; font-weight: 800; color: #D4AF37;">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div style="color: #39FF14; font-size: 1.5rem; font-weight: 900; border: 1px solid #39FF14; padding: 5px 15px; border-radius: 20px; display: inline-block; background: rgba(0,0,0,0.5);">$ {p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}"):
            st.toast(f"Procesando: {p['nombre_producto']}")