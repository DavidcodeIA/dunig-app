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

# Inicialización de estado para evitar el AttributeError
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
# 2. CSS DE ALTA PRECISIÓN (SIN BARRA LATERAL)
# ==========================================
st.markdown("""
    <style>
    /* ELIMINAR BARRA DE DESPLAZAMIENTO Y MÁRGENES */
    html, body, [data-testid="stAppViewBlockContainer"] {
        overflow: hidden !important; /* Adiós barra lateral */
        margin: 0 !important;
        padding: 0 !important;
    }

    .main { background-color: #000000 !important; }
    header { visibility: hidden; display: none !important; }
    footer { visibility: hidden; }
    
    [data-testid="stAppViewBlockContainer"] {
        margin-top: -100px !important; /* Elimina espacio superior de Screenshot_20260509-142706.jpg */
        max-width: 100% !important;
    }

    /* CONTENEDOR DE DESPLAZAMIENTO TÁCTIL (SNAP) */
    [data-testid="stVerticalBlock"] {
        scroll-snap-type: y mandatory;
        overflow-y: scroll !important;
        height: 110vh; /* Un poco más alto para asegurar el flujo */
        gap: 0rem !important;
        -ms-overflow-style: none;  /* Ocultar barra en IE/Edge */
        scrollbar-width: none;  /* Ocultar barra en Firefox */
    }

    /* Ocultar barra en Chrome/Brave/Safari */
    [data-testid="stVerticalBlock"]::-webkit-scrollbar {
        display: none !important;
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
        object-fit: cover; /* 1080x1920 Full Screen */
    }

    /* BOTONES FLOTANTES MEJORADOS */
    div.stButton > button[key^="back_"] {
        position: fixed;
        top: 30px !important; 
        left: 20px !important;
        z-index: 2000 !important;
        background: rgba(0, 0, 0, 0.7) !important;
        color: #FF5F1F !important; 
        border: 2px solid #FF5F1F !important;
        border-radius: 50px !important;
        font-weight: 900 !important;
        padding: 8px 25px !important;
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
        height: 80px !important;
        width: 100% !important;
        font-size: 1.6rem !important;
    }

    .floating-info {
        position: absolute;
        bottom: 120px;
        left: 25px;
        z-index: 500;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. GESTOR DE AUDIO FOCUS (JAVASCRIPT)
# ==========================================
st.components.v1.html("""
<script>
    const manageAudio = () => {
        const videos = window.parent.document.querySelectorAll('video');
        const vh = window.parent.innerHeight;
        videos.forEach(v => {
            const rect = v.getBoundingClientRect();
            // Foco de audio: solo el video visible suena
            if (rect.top >= -50 && rect.top <= 50) { 
                v.muted = false;
                v.play().catch(() => {}); 
            } else {
                v.muted = true;
            }
        });
    };
    
    // Activar al primer toque
    window.parent.document.addEventListener('touchstart', () => {
        const videos = window.parent.document.querySelectorAll('video');
        videos.forEach(v => { v.play().catch(() => {}); });
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
        
        # Botón único de Atrás (Arriba a la izquierda)
        if st.button("⬅ ATRÁS", key="back_master"):
            ir_a('mall')

        for idx, p in enumerate(prods):
            st.markdown(f"""
                <div class="snap-section">
                    <video class="tiktok-video" loop playsinline muted>
                        <source src="{p['video_url']}" type="video/mp4">
                    </video>
                    <div class="floating-info">
                        <div style="font-size: 2.2rem; font-weight: 800; color: #D4AF37; text-shadow: 2px 2px 10px #000;">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                        <div style="color: #39FF14; font-size: 1.8rem; font-weight: 900; border: 2px solid #39FF14; padding: 10px 25px; border-radius: 50px; background: rgba(0,0,0,0.8); display: inline-block;">$ {p['precio']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}"):
                st.toast(f"Procesando pedido para {p['nombre_producto']}...")