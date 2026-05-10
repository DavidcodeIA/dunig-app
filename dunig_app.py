import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

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
# 2. CSS REFORZADO PARA VISIBILIDAD TOTAL
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    
    .video-wrapper {
        position: relative; width: 100%; max-width: 400px;
        margin: auto; background-color: #000;
        border-radius: 25px; border: 2px solid #D4AF37; overflow: hidden;
    }

    /* CAPA DE INFORMACIÓN - REFORZADA */
    .video-info-overlay {
        position: absolute;
        bottom: 20px; /* Lo subimos un poco más */
        left: 15px; 
        right: 15px;
        padding: 15px;
        /* Fondo oscuro semi-transparente para asegurar legibilidad */
        background: rgba(0, 0, 0, 0.6); 
        backdrop-filter: blur(5px);
        border-radius: 15px;
        z-index: 99;
        pointer-events: none;
        display: flex;
        flex-direction: column;
        border-left: 4px solid #D4AF37; /* Detalle luxury */
    }

    .shop-name-tag {
        color: #aaaaaa; font-size: 0.85rem; font-weight: 400;
        text-transform: lowercase; letter-spacing: 1px;
    }

    .product-title-tag {
        color: #ffffff; font-size: 1.4rem; font-weight: 800;
        text-transform: uppercase; margin: 2px 0;
        line-height: 1.1;
    }

    .price-badge {
        color: #39FF14; font-size: 1.3rem; font-weight: 900;
        text-shadow: 0px 0px 10px rgba(57, 255, 20, 0.5);
    }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        color: #000 !important; border-radius: 15px !important;
        font-weight: 800 !important; height: 50px; margin-top: 10px !important;
    }

    video { width: 100% !important; height: auto !important; object-fit: cover !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE NAVEGACIÓN
# ==========================================
if st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    for t in tiendas:
        if st.button(f"ENTRAR A {t['nombre_comercio'].upper()}", use_container_width=True):
            st.session_state.tienda_actual = t
            ir_a('tienda')

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.button("⬅️ VOLVER", on_click=lambda: ir_a('mall'))
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        # --- EL VIDEO CON LA INFO REFORZADA ---
        st.markdown(f'''
            <div class="video-wrapper">
                <div class="video-info-overlay">
                    <div class="shop-name-tag">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div class="product-title-tag">{p['nombre_producto']}</div>
                    <div class="price-badge">${p['precio']}</div>
                </div>
        ''', unsafe_allow_html=True)
        
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Botón de Compra
        if st.button(f"🛒 ADQUIRIR AHORA", key=f"btn_{p['id']}", use_container_width=True):
            st.toast(f"Redirigiendo a pago de {p['nombre_producto']}...")
        st.divider()