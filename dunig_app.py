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
        return None

supabase = init_connection()

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS DE ALTA PRECISIÓN (ELIMINA EL ESPACIO SUPERIOR)
# ==========================================
st.markdown("""
    <style>
    /* 1. ELIMINAR EL "GHOST SPACE" DE ARRIBA */
    .main { background-color: #000000 !important; }
    header { visibility: hidden; display: none; }
    footer { visibility: hidden; }
    
    /* Forzar que el bloque de la app empiece en el pixel 0 */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0rem !important;
        margin-top: -60px !important; /* Ajuste crítico para subir todo */
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }

    /* 2. EFECTO MAGNÉTICO (SNAP) */
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

    /* 3. BOTONES FLOTANTES (UI DE LUJO) */
    
    /* ATRÁS (Naranja Neón) */
    div.stButton > button[key^="back_"] {
        position: fixed;
        top: 20px !important; 
        left: 15px !important;
        z-index: 2000 !important;
        background: rgba(0, 0, 0, 0.7) !important;
        color: #FF5F1F !important; 
        border: 2px solid #FF5F1F !important;
        border-radius: 50px !important;
        font-weight: 900 !important;
        height: 45px !important;
        padding: 0px 20px !important;
    }

    /* COMPRAR (Dorado Luxury) */
    div.stButton > button[key^="buy_"] {
        position: fixed;
        bottom: 0px !important;
        left: 0px !important;
        z-index: 1000 !important;
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        color: #000 !important; 
        border-radius: 0px !important; 
        font-weight: 900 !important;
        height: 75px !important;
        width: 100% !important;
        font-size: 1.5rem !important;
    }

    .floating-info {
        position: absolute;
        bottom: 100px;
        left: 20px;
        z-index: 500;
        pointer-events: none;
    }

    ::-webkit-scrollbar { display: none; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE TIENDA
# ==========================================
if st.session_state.view == 'mall':
    # Vista simple de tiendas para no estorbar
    tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
    for t in tiendas:
        st.image(t.get("portada_url", ""), use_container_width=True)
        if st.button(f"ENTRAR A {t['nombre_comercio'].upper()}", key=f"t_{t['id']}", use_container_width=True):
            st.session_state.tienda_actual = t
            ir_a('tienda')

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    if st.button("⬅ ATRÁS", key="back_button_fixed"):
        ir_a('mall')

    for idx, p in enumerate(prods):
        # Seccion Snap con Audio Focus habilitado (autoplay sin mute)
        st.markdown(f"""
            <div class="snap-section">
                <video class="tiktok-video" autoplay loop playsinline>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                <div class="floating-info">
                    <div style="font-size: 2rem; font-weight: 800; color: #D4AF37; text-shadow: 2px 2px 8px #000;">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div style="color: #39FF14; font-size: 1.6rem; font-weight: 900; border: 2px solid #39FF14; padding: 8px 20px; border-radius: 50px; display: inline-block; background: rgba(0,0,0,0.7);">$ {p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}"):
            # Aquí va tu ventana_pago anterior
            st.toast(f"Añadido: {p['nombre_producto']}")