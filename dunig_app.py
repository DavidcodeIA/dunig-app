import streamlit as st
from supabase import create_client, Client
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
# 2. ESTÉTICA LUXURY SIN FONDO (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    header {visibility: hidden;}
    
    [data-testid="stAppViewBlockContainer"] {
        padding: 0rem !important;
        max-width: 100% !important;
    }

    /* Contenedor de Video */
    .tiktok-container {
        position: relative;
        width: 100vw;
        height: 85vh; 
        overflow: hidden;
        background: #000;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Botón Regresar Minimalista (Dentro del video, sin fondo) */
    .btn-regresar-mini {
        position: absolute;
        top: 20px;
        left: 20px;
        z-index: 100;
        background: transparent;
        color: rgba(255,255,255,0.7);
        font-size: 24px;
        cursor: pointer;
        border: none;
        text-decoration: none;
        font-family: sans-serif;
    }

    /* Overlay de Información */
    .info-overlay {
        position: absolute;
        bottom: 30px;
        left: 20px;
        z-index: 10;
        pointer-events: none;
    }

    .store-name { 
        font-weight: 800; 
        font-size: 1.4rem; 
        color: #D4AF37; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
        margin: 0;
    }
    
    .product-name {
        font-size: 1.1rem;
        color: #FFFFFF;
        opacity: 0.9;
        margin-bottom: 10px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.9);
    }

    .price-tag-neon {
        background: rgba(0, 0, 0, 0.5);
        color: #39FF14;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.3rem;
        border: 2px solid #39FF14;
        display: inline-block;
    }

    /* Botón de Compra Directo */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important;
        font-weight: 900 !important;
        height: 65px !important;
        border: none !important;
        width: 100% !important;
        font-size: 1.2rem !important;
    }

    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. NAVEGACIÓN
# ==========================================

if st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37; padding:20px;'>🏙️ D'UNIG MALL</h1>", unsafe_allow_html=True)
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
    
    for idx, p in enumerate(prods):
        # VIDEO CON BOTÓN VOLVER TRANSPARENTE E INFO COMPLETA
        st.markdown(f"""
            <div class="tiktok-container">
                <!-- Botón regresar sin fondo -->
                <a href="javascript:window.location.reload();" class="btn-regresar-mini" onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'back'}}, '*')">
                    ❮
                </a>
                
                <video class="tiktok-video" autoplay loop muted playsinline controls>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>

                <div class="info-overlay">
                    <p class="store-name">@{t['nombre_comercio'].replace(" ", "").lower()}</p>
                    <p class="product-name">{p['nombre_producto']}</p>
                    <div class="price-tag-neon">${p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Lógica invisible para el botón de regresar
        if st.button("ATRÁS", key=f"back_btn_{idx}"):
            ir_a('mall')

        # Botón de Compra
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            # Aquí iría tu ventana de pago (st.dialog)
            pass
            
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)