import streamlit as st
from supabase import create_client, Client
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="centered", 
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
# 2. ESTÉTICA "FULL TIKTOK" (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    header { visibility: hidden; }
    
    /* Contenedor de Video Full Screen */
    .video-wrapper {
        position: relative;
        width: 100vw;
        height: 90vh;
        background: #000;
        overflow: hidden;
    }

    .video-canvas {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* BARRA LATERAL DE ICONOS (Atrás, Compartir, Audio) */
    .side-bar {
        position: absolute;
        right: 15px;
        bottom: 150px;
        display: flex;
        flex-direction: column;
        gap: 25px;
        align-items: center;
        z-index: 100;
    }

    .icon-unit {
        color: white;
        text-align: center;
        font-size: 24px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }
    
    .icon-label {
        font-size: 10px;
        font-weight: bold;
        margin-top: 2px;
    }

    /* INFO INFERIOR (Handle y Producto) */
    .bottom-info {
        position: absolute;
        bottom: 40px;
        left: 20px;
        z-index: 10;
        color: white;
        text-shadow: 2px 2px 8px rgba(0,0,0,1);
    }

    .handle { font-weight: 800; font-size: 1.2rem; color: #D4AF37; }
    .price { 
        color: #39FF14; font-weight: 900; font-size: 1.4rem; 
        border: 2px solid #39FF14; padding: 2px 12px; border-radius: 50px;
        background: rgba(0,0,0,0.5);
    }

    /* BOTÓN DE COMPRA ESTILO BARRA */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important;
        font-weight: 800 !important;
        height: 60px !important;
        border: none !important;
        width: 100% !important;
        font-size: 1.1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS
# ==========================================
@st.dialog("💎 CARRITO D'UNIG")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL", f"${total:,.2f}")
    st.divider()
    ref = st.text_input("Ref. de Pago")
    if st.button("🚀 FINALIZAR PEDIDO"):
        if ref:
            msj = f"💎 *PEDIDO*\n📦 {producto['nombre_producto']}\n💰 Total: ${total}\n🎫 Ref: {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("IR A WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. VISTAS
# ==========================================

# --- MALL ---
if st.session_state.view == 'mall':
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
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

# --- TIENDA (FULL TIKTOK UI) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for idx, p in enumerate(prods):
        # HTML del Video y la Interfaz Lateral
        st.markdown(f"""
            <div class="video-wrapper">
                <video class="video-canvas" autoplay loop muted playsinline>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                
                <!-- Barra de Iconos Lateral -->
                <div class="side-bar">
                    <div class="icon-unit">📤<div class="icon-label">Share</div></div>
                    <div class="icon-unit">🎵<div class="icon-label">Audio</div></div>
                    <div class="icon-unit">➕<div class="icon-label">Lista</div></div>
                </div>

                <!-- Info Inferior -->
                <div class="bottom-info">
                    <div class="handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div style="margin-bottom:10px;">{p['nombre_producto']}</div>
                    <span class="price">${p['precio']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Barra de Botones de Acción (Atrás y Comprar)
        c_back, c_buy = st.columns([1, 4])
        with c_back:
            if st.button("⬅️", key=f"back_{idx}", help="Volver al Mall"):
                ir_a('mall')
        with c_buy:
            if st.button(f"🛒 ADQUIRIR AHORA", key=f"buy_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
        
        st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)