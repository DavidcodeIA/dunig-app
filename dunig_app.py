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

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

@st.cache_resource 
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception: return None

supabase = init_connection()

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS "NEÓN & FLOAT" (UI DE LUJO)
# ==========================================
st.markdown("""
    <style>
    /* Reset total de márgenes */
    html, body, [data-testid="stAppViewBlockContainer"] {
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100vw !important;
    }
    .main { background-color: #000 !important; }
    header, footer { visibility: hidden; display: none !important; }
    
    [data-testid="stAppViewBlockContainer"] {
        margin-top: -100px !important; 
        max-width: 100vw !important;
    }

    /* Contenedor con Iman (Snap) */
    [data-testid="stVerticalBlock"] {
        scroll-snap-type: y mandatory;
        overflow-y: scroll !important;
        height: 100vh;
        gap: 0rem !important;
        scrollbar-width: none;
    }
    [data-testid="stVerticalBlock"]::-webkit-scrollbar { display: none; }

    .snap-section {
        scroll-snap-align: start;
        scroll-snap-stop: always;
        position: relative;
        width: 100vw;
        height: 100vh;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* BURBUJA COMPRAR - NEÓN DORADO */
    div.stButton > button[key^="buy_"] {
        position: absolute;
        bottom: 180px !important; /* Arriba del precio */
        left: 20px !important;
        z-index: 1000 !important;
        background: rgba(0,0,0,0.8) !important;
        color: #D4AF37 !important;
        border: 2px solid #D4AF37 !important;
        border-radius: 50px !important;
        box-shadow: 0 0 15px #D4AF37, inset 0 0 5px #D4AF37 !important;
        font-weight: 900 !important;
        width: auto !important;
        padding: 10px 30px !important;
        font-size: 1.2rem !important;
        text-transform: uppercase;
    }

    /* Info Overlay (Precio y Handle) */
    .floating-info {
        position: absolute;
        bottom: 80px;
        left: 20px;
        z-index: 500;
        pointer-events: none;
    }

    .user-tag { font-size: 1.5rem; font-weight: 800; color: white; text-shadow: 2px 2px 5px #000; }
    .price-neon { font-size: 2rem; font-weight: 900; color: #39FF14; text-shadow: 0 0 10px #39FF14; }

    /* Botón ATRÁS */
    div.stButton > button[key^="back_"] {
        position: fixed;
        top: 30px !important;
        left: 20px !important;
        z-index: 2000 !important;
        background: rgba(0,0,0,0.5) !important;
        color: #FF5F1F !important;
        border: 1px solid #FF5F1F !important;
        border-radius: 50px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. SCRIPT DE AUDIO FOCUS (ELIMINA EL MUTE)
# ==========================================
st.components.v1.html("""
<script>
    const activateAudio = () => {
        const videos = window.parent.document.querySelectorAll('video');
        const vh = window.parent.innerHeight;
        videos.forEach(v => {
            const rect = v.getBoundingClientRect();
            if (rect.top >= -100 && rect.top <= 100) {
                v.muted = false;
                v.play().catch(() => {});
            } else {
                v.muted = true;
            }
        });
    };
    window.parent.document.addEventListener('touchstart', () => {
        const videos = window.parent.document.querySelectorAll('video');
        videos.forEach(v => { v.muted = false; v.play(); });
        activateAudio();
    }, { once: true });
    window.parent.addEventListener('scroll', activateAudio);
</script>
""", height=0)

# ==========================================
# 4. CARRITO (DIÁLOGO)
# ==========================================
@st.dialog("💎 PROCESAR PEDIDO")
def ventana_pago(producto, tienda):
    st.write(f"### {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", 1, 100, 1)
    st.metric("Total", f"${float(producto['precio']) * cantidad:,.2f}")
    if st.button("CONFIRMAR WHATSAPP"):
        tel = str(tienda['whatsapp']).strip().replace("+","")
        msj = urllib.parse.quote(f"Hola! Quiero {cantidad} de {producto['nombre_producto']}")
        st.link_button("Ir a WhatsApp", f"https://wa.me/{tel}?text={msj}")

# ==========================================
# 5. RENDERIZADO
# ==========================================
if st.session_state.view == 'mall':
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    for t in tiendas:
        st.image(t['portada_url'])
        if st.button(f"Entrar a {t['nombre_comercio']}", key=f"t_{t['id']}"):
            st.session_state.tienda_actual = t
            ir_a('tienda')

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    if st.button("⬅", key="back_master"): ir_a('mall')

    for p in prods:
        st.markdown(f"""
            <div class="snap-section">
                <video class="tiktok-video" loop playsinline muted>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                <div class="floating-info">
                    <div class="user-tag">@{t['nombre_comercio'].lower()}</div>
                    <div class="price-neon">${p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón Burbuja Neón Dorada (Flotando arriba del precio)
        if st.button("🛒 COMPRAR", key=f"buy_{p['id']}"):
            ventana_pago(p, t)