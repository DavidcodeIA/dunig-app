import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import uuid

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

PLANES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 100}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY MEJORADA (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000000; color: #ffffff; }
    
    /* CÍRCULOS DE PORTADA MÁS GRANDES (200px) */
    .img-redonda {
        width: 200px; height: 200px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 15px auto; display: block;
        box-shadow: 0px 10px 30px rgba(212, 175, 55, 0.3);
    }

    /* CONTENEDOR DE VIDEO RELATIVO */
    .video-wrapper {
        position: relative;
        width: 100%;
        margin-bottom: -10px;
    }

    /* PRECIO: ABAJO A LA IZQUIERDA */
    .price-tag {
        position: absolute;
        bottom: 25px;    /* Dentro del video, parte inferior */
        left: 20px;      /* Esquina izquierda */
        background: rgba(0, 0, 0, 0.8); 
        color: #39FF14; 
        padding: 6px 18px; 
        border-radius: 10px;
        font-weight: 900; 
        border: 2px solid #39FF14; 
        z-index: 100;
        font-size: 1.2rem;
        backdrop-filter: blur(5px);
    }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 50px !important; width: 100% !important;
    }

    .btn-regresar button {
        background: transparent !important; color: #ffffff !important; 
        border: 1px solid rgba(255,255,255,0.3) !important;
        height: 30px !important; font-size: 0.75rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS (TIENDA CORREGIDA)
# ==========================================
if st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    
    # Grid de tiendas con círculos grandes
    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(tiendas):
                t = tiendas[i + j]
                with cols[j]:
                    st.markdown(f'<img src="{t["portada_url"]}" class="img-redonda">', unsafe_allow_html=True)
                    if st.button(f"ENTRAR {t['nombre_comercio'].upper()}", key=f"t_{t['id']}", use_container_width=True):
                        st.session_state.tienda_actual = t
                        ir_a('tienda')

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.markdown('<div class="btn-regresar">', unsafe_allow_html=True)
    if st.button("⬅️ REGRESAR AL MALL"): ir_a('mall')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    for p in prods:
        # CONTENEDOR CON PRECIO ABAJO A LA IZQUIERDA
        st.markdown(f'''
            <div class="video-wrapper">
                <div class="price-tag">${p['precio']}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        
        st.markdown(f"<h3 style='text-align:center;'>{p['nombre_producto']}</h3>", unsafe_allow_html=True)
        
        if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"p_{p['id']}", use_container_width=True):
            # Aquí iría tu ventana_pago(p, t) definida antes
            pass
        st.divider()

# (El Panel Admin se mantiene con su lógica de gestión de productos y pagos)