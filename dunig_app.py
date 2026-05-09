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

# Inicialización de estado segura
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
# 2. CSS "ULTRA-WIDE" (SIN MARCOS LATERALES)
# ==========================================
st.markdown("""
    <style>
    /* ELIMINAR CUALQUIER MARGEN O RELLENO DEL CONTENEDOR DE STREAMLIT */
    html, body, [data-testid="stAppViewBlockContainer"] {
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100vw !important;
    }

    .main { background-color: #000000 !important; }
    header { visibility: hidden; display: none !important; }
    footer { visibility: hidden; }
    
    /* SUCCIONAR ESPACIO SUPERIOR Y ELIMINAR RESTRICCIÓN DE ANCHO */
    [data-testid="stAppViewBlockContainer"] {
        margin-top: -100px !important; 
        max-width: 100vw !important;
        min-width: 100vw !important;
    }

    /* ELIMINAR MARGENES INTERNOS DE LAS COLUMNAS Y BLOQUES */
    [data-testid="stVerticalBlock"] {
        scroll-snap-type: y mandatory;
        overflow-y: scroll !important;
        height: 100vh;
        gap: 0rem !important;
        scrollbar-width: none;
    }
    
    [data-testid="stVerticalBlock"]::-webkit-scrollbar {
        display: none !important;
    }

    /* VIDEO SIN MARCOS (FULL SCREEN 9:16) */
    .snap-section {
        scroll-snap-align: start;
        scroll-snap-stop: always;
        position: relative;
        width: 100vw; /* Ocupa todo el ancho */
        height: 100vh;
        background: #000;
        margin: 0 !important;
        padding: 0 !important;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Asegura que no queden franjas negras */
    }

    /* BOTONES FLOTANTES */
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
    }

    .floating-info {
        position: absolute;
        bottom: 100px;
        left: 20px;
        z-index: 500;
        pointer-events: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. GESTOR DE AUDIO ACTIVO (AUDIO FOCUS)
# ==========================================
st.components.v1.html("""
<script>
    const videos = window.parent.document.querySelectorAll('video');
    
    const manageAudio = () => {
        const vh = window.parent.innerHeight;
        videos.forEach(v => {
            const rect = v.getBoundingClientRect();
            // Si el video está centrado, desmutear y reproducir
            if (rect.top >= -100 && rect.top <= 100) { 
                v.muted = false;
                v.play().catch(e => console.log("Audio bloqueado"));
            } else {
                v.muted = true;
            }
        });
    };
    
    // Desbloquear audio al primer toque en la pantalla
    window.parent.document.addEventListener('touchstart', () => {
        videos.forEach(v => { 
            v.muted = false;
            v.play(); 
        });
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
            if st.button(f"ENTRAR A {t['nombre_comercio'].upper()}", key=f"t_{t['id']}"):
                st.session_state.tienda_actual = t
                ir_a('tienda')

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if supabase and t:
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        
        # Botón Atrás Maestro
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
                st.toast(f"Pedido iniciado: {p['nombre_producto']}")