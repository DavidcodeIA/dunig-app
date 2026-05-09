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

PLANES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA INMERSIVA (CSS)
# ==========================================
st.markdown("""
    <style>
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .stApp { background-color: #000; }
    header, footer { visibility: hidden; }
    
    .video-canvas {
        position: relative;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: #000;
    }

    .stVideo { position: absolute; top: 0; left: 0; width: 100vw !important; height: 100vh !important; }
    .stVideo video { object-fit: cover !important; width: 100vw !important; height: 100vh !important; }

    .ui-overlay {
        position: absolute;
        bottom: 60px;
        left: 25px;
        z-index: 999;
        display: flex;
        flex-direction: column;
        gap: 15px;
        pointer-events: none;
    }

    .ui-overlay button, .ui-overlay .price-tag-luxury { pointer-events: auto !important; }

    .stButton > button {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        font-size: 60px !important;
        color: white !important;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
    }

    .price-tag-luxury {
        background: #FFD700;
        color: black;
        padding: 5px 20px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 2.2rem;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }

    .luxury-text {
        color: #1E4D92;
        font-weight: 900;
        text-transform: uppercase;
        -webkit-text-stroke: 1.5px white;
        margin: 0;
        line-height: 1;
        text-align: left;
    }
    .brand-title { font-size: 2.8rem; }
    .product-title { font-size: 3.2rem; margin-top: -5px; }

    .img-redonda {
        width: 140px; height: 140px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 10px auto; display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DE PAGO
# ==========================================
@st.dialog("💎 PUNTO DE VENTA")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.info(f"💳 **DATOS DE PAGO:**\n{tienda.get('datos_pago', 'Consultar al vendedor')}")
    ref = st.text_input("Ingrese Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO", use_container_width=True):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Producto:* {producto['nombre_producto']}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").replace(" ", "").strip()
            st.link_button("ENVIAR POR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"

if not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG MALL</h1>", unsafe_allow_html=True)
        tiendas = supabase.table("perfiles_comercio").select("*").execute().data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.markdown(f'<img src="{t["portada_url"]}" class="img-redonda">', unsafe_allow_html=True)
                        if st.button(t['nombre_comercio'].upper(), key=f"t_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t; ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        for p in prods:
            st.markdown('<div class="video-canvas">', unsafe_allow_html=True)
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            st.markdown('<div class="ui-overlay">', unsafe_allow_html=True)
            if st.button("↩️", key=f"back_{p['id']}"): ir_a('mall')
            st.markdown(f'<div class="price-tag-luxury">{p["precio"]}$</div>', unsafe_allow_html=True)
            if st.button("💳", key=f"pay_{p['id']}"): ventana_pago(p, t)
            st.