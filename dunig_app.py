import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS ULTRA PRO: FULL WIDTH + NAV BAR
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000; color: #fff; }
    
    /* VIDEO FULL SCREEN WIDTH */
    .video-full {
        width: 100vw;
        position: relative;
        left: 50%;
        right: 50%;
        margin-left: -50vw;
        margin-right: -50vw;
        background: #000;
        line-height: 0;
    }
    
    video { width: 100% !important; height: auto !important; max-height: 80vh; object-fit: cover; }

    /* FILA DE CONTROL (FLECHA + INFO) */
    .control-bar {
        display: flex;
        align-items: center;
        gap: 10px;
        width: 100%;
        max-width: 500px;
        margin: -5px auto 10px auto;
        padding: 0 10px;
    }

    /* Estilo para el botón de flecha blanca (hackeando el botón de Streamlit) */
    div[data-testid="column"]:nth-child(1) button {
        background: transparent !important;
        border: 2px solid #ffffff !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        width: 50px !important;
        height: 50px !important;
        font-size: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .product-details {
        flex-grow: 1;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        padding: 0 15px;
        height: 50px;
        border-radius: 12px;
        border: 1px solid rgba(212, 175, 55, 0.4);
    }

    .txt-name { color: #D4AF37; font-weight: 700; text-transform: uppercase; font-size: 0.9rem; }
    .txt-price { color: #39FF14; font-weight: 900; font-size: 1.1rem; }

    /* BOTÓN COMPRAR DORADO */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important;
        font-weight: 800 !important;
        border-radius: 15px !important;
        height: 55px !important;
        border: none !important;
        transition: 0.3s;
    }
    
    /* Portadas del Mall */
    .img-mall { width: 100%; aspect-ratio: 1/1; object-fit: cover; border-radius: 10px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================

if st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    
    cols = st.columns(2)
    for idx, t in enumerate(tiendas):
        with cols[idx % 2]:
            st.markdown(f'<img src="{t["portada_url"]}" class="img-mall">', unsafe_allow_html=True)
            if st.button(f"ENTRAR {t['nombre_comercio'].upper()}", key=f"t_{t['id']}", use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        # --- VIDEO FULL WIDTH ---
        st.markdown('<div class="video-full">', unsafe_allow_html=True)
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # --- FILA ÚNICA: FLECHA + INFO ---
        # Usamos dos columnas muy pegadas para simular la barra de control
        c1, c2 = st.columns([1, 5])
        
        with c1:
            # Esta es la flecha blanca que ahora SÍ funciona para volver
            if st.button("←", key=f"back_{p['id']}"):
                ir_a('mall')
        
        with c2:
            st.markdown(f'''
                <div class="product-details">
                    <span class="txt-name">{p['nombre_producto']}</span>
                    <span class="txt-price">${p['precio']}</span>
                </div>
            ''', unsafe_allow_html=True)

        # --- BOTÓN COMPRAR ---
        if st.button("🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            msj = f"Hola {t['nombre_comercio']}, quiero comprar {p['nombre_producto']} por ${p['precio']}"
            st.link_button("CONFIRMAR EN WHATSAPP", f"https://wa.me/{t['whatsapp']}?text={urllib.parse.quote(msj)}")
        
        st.divider()