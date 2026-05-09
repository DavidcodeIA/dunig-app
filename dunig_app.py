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
# 2. ESTÉTICA LUXURY (CSS) - PANTALLA COMPLETA
# ==========================================
st.markdown("""
    <style>
    /* Reset total para pantalla completa */
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .stApp { background-color: #000; }
    header, footer { visibility: hidden; }

    /* Contenedor del video como fondo */
    .video-canvas {
        position: relative;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
    }

    .stVideo { position: absolute; top: 0; left: 0; width: 100vw !important; height: 100vh !important; }
    .stVideo video { object-fit: cover !important; width: 100vw !important; height: 100vh !important; }

    /* Capa de iconos flotantes (DENTRO DEL VIDEO) */
    .ui-overlay {
        position: absolute;
        bottom: 50px;
        left: 20px;
        z-index: 999;
        display: flex;
        flex-direction: column;
        gap: 15px;
        pointer-events: none;
    }

    .ui-overlay button, .ui-overlay .price-bubble-float { pointer-events: auto !important; }

    /* Botones invisibles con iconos gigantes */
    .stButton > button {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        font-size: 60px !important;
        color: white !important;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
    }

    /* Burbuja de precio flotante */
    .price-bubble-float {
        background: #FFD700;
        color: black;
        padding: 5px 20px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 2.2rem;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        border: 2px solid #000;
    }

    /* Textos estilo Luxury (Azul con borde blanco) */
    .luxury-text {
        color: #1E4D92;
        font-weight: 900;
        text-transform: uppercase;
        -webkit-text-stroke: 1.5px white;
        margin: 0;
        line-height: 1;
        text-align: left;
    }
    .brand-title { font-size: 2.5rem; }
    .product-title { font-size: 3rem; margin-top: -5px; }

    /* Estilo para el Mall */
    .img-redonda {
        width: 140px; height: 140px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 10px auto; display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DEL CARRITO
# ==========================================
@st.dialog("💎 CARRITO D'UNIG LUXURY")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **DATOS DE PAGO:**\n{tienda.get('datos_pago', 'Consultar al vendedor')}")
    ref = st.text_input("Ingrese Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Producto:* {producto['nombre_producto']}\n🔢 *Cant:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").replace(" ", "").strip()
            st.link_button("ENVIAR POR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else: st.error("Por favor, ingrese la referencia de pago")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE NUEVO SOCIO</h1>", unsafe_allow_html=True)
    # ... (Mantiene tu lógica de formulario de registro intacta)

elif not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37; padding-top:20px;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        res = supabase.table("perfiles_comercio").select("*").execute()
        tiendas = res.data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        url = t.get('portada_url') or "https://via.placeholder.com/150"
                        st.markdown(f'<img src="{url}" class="img-redonda">', unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; color:#D4AF37; font-weight:bold;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                        if st.button("VISITAR", key=f"m_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t