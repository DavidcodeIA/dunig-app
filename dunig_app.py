import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN TOTAL FULL SCREEN
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
# 2. ESTÉTICA INMERSIVA (CSS) - ICONOS DENTRO
# ==========================================
st.markdown("""
    <style>
    /* Eliminar basura de Streamlit y forzar Negro */
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .stApp { background-color: #000; }
    header, footer { visibility: hidden; }
    
    /* Contenedor Maestro: El video es el fondo */
    .video-canvas {
        position: relative;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: #000;
    }

    /* Forzar video a pantalla completa */
    .stVideo { position: absolute; top: 0; left: 0; width: 100vw !important; height: 100vh !important; }
    .stVideo video { object-fit: cover !important; width: 100vw !important; height: 100vh !important; }

    /* CAPA DE INTERFAZ (UI) SOBRE EL VIDEO */
    .ui-overlay {
        position: absolute;
        bottom: 50px;
        left: 20px;
        z-index: 999;
        display: flex;
        flex-direction: column;
        gap: 15px;
        pointer-events: none; /* Deja que el video se vea atrás */
    }

    /* Activar click solo para botones */
    .ui-overlay button, .ui-overlay .price-bubble { pointer-events: auto !important; }

    /* Estilo de los botones transparentes con iconos grandes */
    .stButton > button {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        font-size: 60px !important; /* Iconos gigantes como tu dibujo */
        color: white !important;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
    }

    /* Burbuja de precio estilo tu ejemplo */
    .price-tag-luxury {
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

    /* Textos Traki / Pantalones (Azul con borde blanco) */
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

    /* Mall Styles */
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
@st.dialog("💎 PUNTO DE VENTA")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **DATOS DE PAGO:**\n{tienda.get('datos_pago', 'Consultar al vendedor')}")
    ref = st.text_input("Ingrese Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO", use_container_width=True):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Producto:* {producto['nombre_producto']}\n🔢 *Cant:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").replace(" ", "").strip()
            st.link_button("ENVIAR POR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO SOCIO</h1>", unsafe_allow_html=True)
    # ... (Mantiene tu lógica de formulario de registro)
    with st.form("form_reg"):
        rn = st.text_input("Tienda"); rm = st.text_input("Email"); rt = st.text_input("WhatsApp")
        ri = st.file_uploader("Portada", type=['jpg', 'png']); ref_socio = st.text_input("Ref Pago")
        if st.form_submit_button("REGISTRAR"):
            if rn and ri:
                st.success("Registrado. Notifica al admin.")

elif not es_admin:
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
            # --- ESTRUCTURA DE PANTALLA COMPLETA ---
            st.markdown('<div class="video-canvas">', unsafe_allow_html=True)
            
            # 1. Video de Fondo (TikTok Style)
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)

            # 2. Capa UI (Iconos y Textos DENTRO del video)
            st.markdown('<div class="ui-overlay">', unsafe_allow_html=True)
            
            # Flecha Regresar
            if st.button("↩️", key=f"back_{p['id']}"): ir_a('mall')
            
            # Burbuja de Precio (Dinero)
            st.markdown(f'<div class="price-tag-luxury">{p["precio"]}$</div>', unsafe_allow_html=True)
            
            # Icono Punto de Venta (Pagar)
            if st.button("💳", key=f"pay_{p['id']}"): ventana_pago(p, t)
            
            # Textos de Marca y Producto
            st.markdown(f'<p class="luxury-text brand-title">{t["nombre_comercio"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="luxury-text product-title">{p["nombre_producto"]}</p>', unsafe_allow_html=True)
            
            st.markdown('</div></div>', unsafe_allow_html=True)

else:
    # --- PANEL ADMIN ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL ADMIN</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        m = st.text_input("Email").lower()
        c = st.text_input("Código", type="password").upper()
        if st.button("ENTRAR"):
            res = supabase.table("perfiles_comercio").