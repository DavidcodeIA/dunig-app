import streamlit as st
from supabase import create_client

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA (ESTRICTA)
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Inicialización de estados para evitar AttributeErrors
if 'view' not in st.session_state:
    st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state:
    st.session_state.tienda_actual = None

@st.cache_resource 
def init_connection():
    try:
        # Usa tus secrets de Streamlit Cloud
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except:
        return None

supabase = init_connection()

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS DE ALTA PRECISIÓN (BORDE A BORDE)
# ==========================================
st.markdown("""
    <style>
    /* RESET TOTAL DE STREAMLIT */
    header, footer, [data-testid="stSidebar"] { visibility: hidden; display: none !important; }
    
    html, body, .main, [data-testid="stAppViewBlockContainer"] {
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background-color: #000 !important;
    }

    [data-testid="stAppViewBlockContainer"] {
        margin-top: -100px !important; /* Succiona el espacio del header */
    }

    /* CONTENEDOR VERTICAL CON SNAP MAGNÉTICO */
    [data-testid="stVerticalBlock"] {
        scroll-snap-type: y mandatory;
        overflow-y: scroll !important;
        height: 100vh;
        gap: 0px !important;
        scrollbar-width: none;
    }
    [data-testid="stVerticalBlock"]::-webkit-scrollbar { display: none !important; }

    /* DISEÑO MALL: PANTALLA DIVIDIDA (SPLIT) */
    .split-container {
        display: flex;
        flex-direction: column;
        height: 100vh;
        width: 100vw;
    }
    .shop-half {
        height: 50vh;
        width: 100vw;
        position: relative;
        overflow: hidden;
    }
    .shop-half img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .shop-label {
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 2.5rem;
        font-weight: 900;
        text-shadow: 2px 2px 20px #000;
        text-transform: uppercase;
        letter-spacing: 4px;
        pointer-events: none;
        z-index: 5;
    }

    /* DISEÑO TIENDA: VIDEO TIKTOK FULL */
    .snap-section {
        scroll-snap-align: start;
        scroll-snap-stop: always;
        position: relative;
        width: 100vw;
        height: 100vh;
        background: #000;
    }
    video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* UI FLOTANTE (BOTONES) */
    div.stButton > button[key^="link_"] {
        width: 100vw !important; height: 50vh !important;
        background: transparent !important; border: none !important;
        position: absolute; top: 0; z-index: 10; color: transparent !important;
    }
    div.stButton > button[key^="back_"] {
        position: fixed; top: 40px; left: 20px; z-index: 2000;
        background: rgba(0,0,0,0.7) !important; color: #FF5F1F !important;
        border: 2px solid #FF5F1F !important; border-radius: 50px !important;
        font-weight: 900;
    }
    div.stButton > button[key^="buy_"] {
        position: fixed; bottom: 0; left: 0; z-index: 1000;
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295);
        color: #000 !important; font-weight: 900; height: 80px; width: 100%;
        font-size: 1.5rem !important; border-radius: 0px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. JS: AUDIO FOCUS & AUTO-PLAY
# ==========================================
st.components.v1.html("""
<script>
    const setupAudio = () => {
        const videos = window.parent.document.querySelectorAll('video');
        const vh = window.parent.innerHeight;
        
        videos.forEach(v => {
            const rect = v.getBoundingClientRect();
            // Si el video está centrado (Foco de Audio)
            if (rect.top >= -100 && rect.top <= 100) {
                v.muted = false;
                v.play().catch(()=>{});
            } else {
                v.muted = true;
                v.pause();
            }
        });
    };

    // Desbloqueo inicial al tocar la pantalla (Vital para Brave/Chrome)
    window.parent.document.addEventListener('touchstart', () => {
        window.parent.document.querySelectorAll('video').forEach(v => {
            v.muted = false;
            v.play().catch(()=>{});
        });
        setupAudio();
    }, { once: true });

    window.parent.addEventListener('scroll', setupAudio);
</script>
""", height=0)

# ==========================================
# 4. LÓGICA DE NAVEGACIÓN
# ==========================================

# VISTA 1: EL MALL (TIENDAS DIVIDIDAS)
if st.session_state.view == 'mall':
    if supabase:
        # Traemos las 2 tiendas principales para el split screen
        tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).limit(2).execute().data
        
        for idx, t in enumerate(tiendas):
            st.markdown(f"""
                <div class="shop-half">
                    <img src="{t.get('portada_url', '')}">
                    <div class="shop-label">{t['nombre_comercio']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Botón invisible sobre la mitad de la pantalla
            if st.button(f"Entrar {idx}", key=f"link_{t['id']}"):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# VISTA 2: LA TIENDA (FEED DE VIDEOS TIKTOK)
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if supabase and t:
        # Cargar productos de la tienda seleccionada
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        
        if st.button("⬅ VOLVER", key="back_master"):
            ir_a('mall')

        for idx, p in enumerate(prods):
            st.markdown(f"""
                <div class="snap-section">
                    <video class="tiktok-video" loop playsinline muted preload="auto">
                        <source src="{p['video_url']}" type="video/mp4">
                    </video>
                    <div style="position:absolute; bottom:120px; left:25px; z-index:500; text-shadow: 2px 2px 10px #000;">
                        <h1 style="color:#D4AF37; margin:0; font-size:2.5rem;">@{t['nombre_comercio'].replace(" ","").lower()}</h1>
                        <p style="color:#FFF; font-size:1.2rem; margin:5px 0;">{p['nombre_producto']}</p>
                        <h2 style="color:#39FF14; font-weight:900; background:rgba(0,0,0,0.5); display:inline-block; padding:5px 15px; border-radius:10px;">$ {p['precio']}</h2>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}"):
                st.toast(f"¡{p['nombre_producto']} añadido al carrito!")