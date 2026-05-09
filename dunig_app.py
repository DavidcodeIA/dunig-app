import streamlit as st
from supabase import create_client
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Inicialización segura del estado (Evita el AttributeError)
if 'view' not in st.session_state:
    st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state:
    st.session_state.tienda_actual = None

@st.cache_resource 
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

supabase = init_connection()

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. AUDIO FOCUS & UI FULL-SCREEN (CSS)
# ==========================================
st.markdown("""
    <style>
    /* ELIMINAR ESPACIO SUPERIOR DE RAÍZ */
    .main { background-color: #000000 !important; }
    header { visibility: hidden; display: none !important; }
    footer { visibility: hidden; }
    
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0rem !important;
        margin-top: -85px !important; /* Succiona el espacio del título */
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }

    /* MECÁNICA DE PEGADO (SCROLL SNAPPING) */
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
        object-fit: cover; /* Formato 9:16 sin bordes negros */
    }

    /* BOTONES FLOTANTES */
    div.stButton > button[key^="back_"] {
        position: fixed;
        top: 25px !important; 
        left: 15px !important;
        z-index: 2000 !important;
        background: rgba(0, 0, 0, 0.7) !important;
        color: #FF5F1F !important; 
        border: 2px solid #FF5F1F !important;
        border-radius: 50px !important;
        font-weight: 900 !important;
        padding: 5px 20px !important;
    }

    div.stButton > button[key^="buy_"] {
        position: fixed;
        bottom: 0px !important;
        left: 0px !important;
        z-index: 1000 !important;
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        color: #000 !important; 
        border: none !important;
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
# 3. GESTOR DE AUDIO (JAVASCRIPT)
# ==========================================
st.components.v1.html("""
<script>
    function manageAudio() {
        const videos = window.parent.document.querySelectorAll('video');
        const vh = window.parent.innerHeight;
        videos.forEach(v => {
            const rect = v.getBoundingClientRect();
            // Solo suena el video en el centro de la pantalla (Audio Focus)
            if (rect.top >= 0 && rect.bottom <= vh) {
                v.muted = false;
                v.play();
            } else {
                v.muted = true;
            }
        });
    }
    window.parent.document.addEventListener('click', () => {
        const videos = window.parent.document.querySelectorAll('video');
        videos.forEach(v => { v.muted = false; v.play(); });
        manageAudio();
    }, { once: true });
    window.parent.addEventListener('scroll', manageAudio);
</script>
""", height=0)

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
if st.session_state.view == 'mall':
    if supabase:
        tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
        for t in tiendas:
            st.image(t.get("portada_url", ""), use_container_width=True)
            if st.button(f"ENTRAR A {t['nombre_comercio'].upper()}", key=f"t_{t['id']}", use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if supabase and t:
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        
        # Botón único de Atrás
        if st.button("⬅ ATRÁS", key="back_master"):
            ir_a('mall')

        for idx, p in enumerate(prods):
            st.markdown(f"""
                <div class="snap-section">
                    <video class="tiktok-video" loop playsinline muted>
                        <source src="{p['video_url']}" type="video/mp4">
                    </video>
                    <div class="floating-info">
                        <div style="font-size: 2rem; font-weight: 800; color: #D4AF37;">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                        <div style="color: #39FF14; font-size: 1.6rem; font-weight: 900; border: 2px solid #39FF14; padding: 8px 20px; border-radius: 50px; background: rgba(0,0,0,0.7); display: inline-block;">$ {p['precio']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}"):
                st.toast(f"Procesando: {p['nombre_producto']}")