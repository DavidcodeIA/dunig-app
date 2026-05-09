import streamlit as st
from supabase import create_client

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Inicialización segura del estado
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
# 2. CSS "ULTRA-INMERSIVO" (SIN BARRAS NI MARCOS)
# ==========================================
st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit */
    header, footer, [data-testid="stSidebar"] { visibility: hidden; display: none !important; }
    
    /* Eliminar scrollbars y márgenes globales */
    html, body, .main, [data-testid="stAppViewBlockContainer"] {
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background-color: #000 !important;
    }

    /* Forzar que el contenedor principal empiece desde arriba (Elimina espacio del título) */
    [data-testid="stAppViewBlockContainer"] {
        margin-top: -100px !important; 
        max-width: 100vw !important;
    }

    /* Contenedor de Scroll Magnético (Snap) */
    [data-testid="stVerticalBlock"] {
        scroll-snap-type: y mandatory;
        overflow-y: scroll !important;
        height: 100vh;
        gap: 0px !important;
        scrollbar-width: none; /* Firefox */
        -ms-overflow-style: none; /* IE/Edge */
    }

    [data-testid="stVerticalBlock"]::-webkit-scrollbar {
        display: none !important; /* Chrome/Brave/Safari */
    }

    /* Estilo de Video TikTok */
    .snap-section {
        scroll-snap-align: start;
        scroll-snap-stop: always;
        position: relative;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Llena la pantalla sin barras negras */
    }

    /* Botones UI de Lujo */
    div.stButton > button[key^="back_"] {
        position: fixed; top: 30px; left: 20px; z-index: 1000;
        background: rgba(0, 0, 0, 0.6) !important; color: #FF5F1F !important;
        border: 2px solid #FF5F1F !important; border-radius: 50px !important;
        font-weight: 900 !important; padding: 5px 20px !important;
    }

    div.stButton > button[key^="buy_"] {
        position: fixed; bottom: 0; left: 0; z-index: 999;
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295);
        color: #000 !important; border: none !important;
        font-weight: 900 !important; height: 75px !important;
        width: 100% !important; font-size: 1.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. SCRIPT AUDIO FOCUS & REPRODUCCIÓN
# ==========================================
st.components.v1.html("""
<script>
    const manageAudio = () => {
        const videos = window.parent.document.querySelectorAll('video');
        const vh = window.parent.innerHeight;
        videos.forEach(v => {
            const rect = v.getBoundingClientRect();
            // Si el video ocupa la pantalla central (Foco de Audio)
            if (rect.top >= -100 && rect.top <= 100) { 
                v.muted = false;
                v.play().catch(e => {}); 
            } else {
                v.muted = true;
                v.pause();
            }
        });
    };
    
    // Desbloquear audio al primer toque (Interacción requerida por Brave/Chrome)
    window.parent.document.addEventListener('touchstart', () => {
        window.parent.document.querySelectorAll('video').forEach(v => v.play());
        manageAudio();
    }, { once: true });

    window.parent.addEventListener('scroll', manageAudio);
</script>
""", height=0)

# ==========================================
# 4. LÓGICA DE TIENDA
# ==========================================
if st.session_state.view == 'mall':
    # [Aquí mantienes tu lógica de tiendas divididas]
    pass

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if supabase and t:
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        
        # Botón para regresar
        if st.button("⬅ ATRÁS", key="back_btn"):
            ir_a('mall')

        for idx, p in enumerate(prods):
            st.markdown(f"""
                <div class="snap-section">
                    <video class="tiktok-video" loop playsinline muted>
                        <source src="{p['video_url']}" type="video/mp4">
                    </video>
                    <div style="position: absolute; bottom: 100px; left: 20px; color: white; text-shadow: 2px 2px 10px #000; z-index: 500;">
                        <h1 style="margin:0; font-size: 2.2rem; color: #D4AF37;">@{t['nombre_comercio'].replace(" ", "").lower()}</h1>
                        <h2 style="margin:0; color: #39FF14;">$ {p['precio']}</h2>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{idx}"):
                st.toast(f"Procesando: {p['nombre_producto']}")