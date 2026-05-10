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
# 2. ESTÉTICA LUXURY (PRECIO DENTRO DEL VIDEO)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000; color: #fff; }
    
    /* CONTENEDOR MAESTRO DEL VIDEO */
    .video-wrapper {
        position: relative;
        width: 100%;
        border-radius: 15px;
        overflow: hidden; /* Esto asegura que nada se salga del cuadro */
        border: 1px solid rgba(212, 175, 55, 0.3);
    }

    /* BURBUJA DENTRO DEL CUADRO - ESQUINA INFERIOR DERECHA */
    .price-tag {
        position: absolute;
        bottom: 15px;
        right: 15px;
        background: rgba(0, 0, 0, 0.75);
        color: #39FF14;
        padding: 5px 12px;
        border-radius: 10px;
        font-weight: 900;
        font-size: 1.2rem;
        z-index: 99; /* Por encima del video */
        border: 1px solid #39FF14;
        backdrop-filter: blur(4px);
    }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 50px !important; width: 100% !important; margin-top: 10px;
    }

    .btn-regresar button {
        background: transparent !important; color: #fff !important; 
        border: 1px solid rgba(255,255,255,0.2) !important;
        height: 30px !important; font-size: 0.7rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VISTA TIENDA (CARRITO Y VIDEO CORREGIDO)
# ==========================================
if st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    
    # Botón regresar minimalista
    st.markdown('<div class="btn-regresar">', unsafe_allow_html=True)
    if st.button("⬅️ MALL"): ir_a('mall')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        # AQUÍ ESTÁ EL TRUCO: El div envuelve al video y a la etiqueta
        st.markdown(f'''
            <div class="video-wrapper">
                <div class="price-tag">${p['precio']}</div>
            </div>
        ''', unsafe_allow_html=True)
        
        # El video se renderiza justo debajo pero el CSS lo mantiene en el mismo espacio visual
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        
        st.markdown(f"<h3 style='text-align:center;'>{p['nombre_producto']}</h3>", unsafe_allow_html=True)
        
        # Botón de Compra con el Carrito (ventana_pago debe estar definida)
        if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"p_{p['id']}", use_container_width=True):
            # Aquí llamas a tu función @st.dialog ventana_pago(p, t)
            pass 
        st.divider()

# (El resto del código del Mall y Panel Admin se mantiene igual)