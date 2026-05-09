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

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

@st.cache_resource 
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

supabase = init_connection()

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS "SPLIT-SCREEN" & FULL BORDERLESS
# ==========================================
st.markdown("""
    <style>
    /* ELIMINAR TODO EL MARCO DE STREAMLIT */
    [data-testid="stAppViewBlockContainer"] {
        padding: 0px !important;
        margin-top: -100px !important; /* Succiona el header */
        max-width: 100vw !important;
    }
    
    .main { background-color: #000; }
    header, footer { visibility: hidden; }

    /* CONTENEDOR DE TIENDAS DIVIDIDAS (MALL) */
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
        cursor: pointer;
    }

    .shop-half img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .shop-label {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        color: white;
        font-size: 2rem;
        font-weight: 900;
        text-shadow: 2px 2px 15px #000;
        text-transform: uppercase;
        letter-spacing: 5px;
        pointer-events: none;
    }

    /* ESTILO TIKTOK PARA VIDEOS (TIENDA) */
    [data-testid="stVerticalBlock"] {
        scroll-snap-type: y mandatory;
        overflow-y: scroll !important;
        height: 100vh;
        gap: 0px !important;
    }
    
    [data-testid="stVerticalBlock"]::-webkit-scrollbar { display: none; }

    .snap-section {
        scroll-snap-align: start;
        scroll-snap-stop: always;
        width: 100vw;
        height: 100vh;
        background: #000;
    }

    video { width: 100%; height: 100%; object-fit: cover; }

    /* BOTONES FLOTANTES */
    div.stButton > button[key^="btn_"] {
        width: 100% !important; height: 50vh !important;
        background: transparent !important; border: none !important;
        position: absolute; top: 0; z-index: 10;
    }

    div.stButton > button[key^="back_"] {
        position: fixed; top: 30px; left: 20px; z-index: 2000;
        background: rgba(0,0,0,0.7) !important; color: #FF5F1F !important;
        border: 2px solid #FF5F1F !important; border-radius: 50px !important;
    }

    div.stButton > button[key^="buy_"] {
        position: fixed; bottom: 0; left: 0; z-index: 1000;
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295);
        color: #000 !important; font-weight: 900; height: 80px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE AUDIO FOCUS (Técnica TikTok)
# ==========================================
st.components.v1.html("""
<script>
    const manageAudio = () => {
        const videos = window.parent.document.querySelectorAll('video');
        const vh = window.parent.innerHeight;
        videos.forEach(v => {
            const rect = v.getBoundingClientRect();
            if (rect.top >= -50 && rect.top <= 50) { 
                v.muted = false; v.play().catch(()=>{}); 
            } else { v.muted = true; }
        });
    };
    window.parent.document.addEventListener('touchstart', () => {
        window.parent.document.querySelectorAll('video').forEach(v => v.play());
        manageAudio();
    }, { once: true });
    window.parent.addEventListener('scroll', manageAudio);
</script>
""", height=0)

# ==========================================
# 4. VISTAS
# ==========================================
if st.session_state.view == 'mall':
    if supabase:
        tiendas = supabase.table("perfiles_comercio").select("*").limit(2).execute().data
        for idx, t in enumerate(tiendas):
            st.markdown(f"""
                <div class="shop-half">
                    <img src="{t.get('portada_url', '')}">
                    <div class="shop-label">{t['nombre_comercio']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("", key=f"btn_{t['id']}"):
                st.session_state.tienda_actual = t
                ir_a('tienda')

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if supabase and t:
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        if st.button("⬅ ATRÁS", key="back_master"): ir_a('mall')
        
        for p in prods:
            st.markdown(f"""
                <div class="snap-section">
                    <video loop playsinline muted><source src="{p['video_url']}"></video>
                    <div style="position:absolute; bottom:120px; left:20px; z-index:500;">
                        <h1 style="color:#D4AF37; margin:0;">@{t['nombre_comercio']}</h1>
                        <h2 style="color:#39FF14;">$ {p['precio']}</h2>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"🛒 COMPRAR", key=f"buy_{p['id']}"): st.toast("Añadido")