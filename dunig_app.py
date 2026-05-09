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
# 2. ESTÉTICA TIKTOK LUXURY FULL (CSS)
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
        height: 85vh; /* Espacio para la barra inferior */
        background: #000;
        overflow: hidden;
    }

    .video-canvas {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* INFO INFERIOR (Handle y Producto) */
    .bottom-info {
        position: absolute;
        bottom: 20px;
        left: 20px;
        z-index: 10;
        color: white;
        text-shadow: 2px 2px 8px rgba(0,0,0,1);
    }

    .handle { font-weight: 800; font-size: 1.2rem; color: #D4AF37; margin-bottom: 5px; }
    .price-bubble { 
        color: #39FF14; font-weight: 900; font-size: 1.4rem; 
        border: 2px solid #39FF14; padding: 2px 12px; border-radius: 50px;
        background: rgba(0,0,0,0.6); display: inline-block;
    }

    /* BARRA DE NAVEGACIÓN INFERIOR (ESTÁTICA) */
    .nav-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 70px;
        background-color: #000;
        display: flex;
        justify-content: space-around;
        align-items: center;
        border-top: 0.5px solid #333;
        z-index: 1000;
    }

    .nav-item {
        color: white;
        text-align: center;
        flex: 1;
        font-size: 0.7rem;
        opacity: 0.8;
    }

    .nav-icon { font-size: 1.5rem; margin-bottom: 2px; }

    .plus-btn {
        background-color: white;
        color: black;
        border-radius: 8px;
        padding: 5px 15px;
        font-size: 1.2rem;
        font-weight: bold;
    }

    /* Botón de Compra Flotante */
    .buy-container {
        padding: 10px;
        background: #000;
    }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 10px !important;
        font-weight: 800 !important;
        height: 50px !important;
        border: none !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS (CARRITO)
# ==========================================
@st.dialog("💎 CARRITO D'UNIG")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL", f"${total:,.2f}")
    st.divider()
    ref = st.text_input("Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"💎 *PEDIDO*\n📦 {producto['nombre_producto']}\n💰 Total: ${total}\n🎫 Ref: {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("IR A WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================

# --- MALL (VISTA PRINCIPAL) ---
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

# --- TIENDA (UI TIKTOK MEJORADA) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for idx, p in enumerate(prods):
        # Video y Overlay
        st.markdown(f"""
            <div class="video-wrapper">
                <video class="video-canvas" autoplay loop muted playsinline>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                <div class="bottom-info">
                    <div class="handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div style="margin-bottom:10px;">{p['nombre_producto']}</div>
                    <span class="price-bubble">${p['precio']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón de Compra debajo del video
        if st.button(f"🛒 COMPRAR {p['nombre_producto'].upper()}", key=f"buy_{p['id']}", use_container_width=True):
            ventana_pago(p, t)
        
        st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)

# ==========================================
# 5. BARRA DE NAVEGACIÓN INFERIOR (PERMANENTE)
# ==========================================
# Definimos las columnas para capturar los clics de los botones de la barra
st.markdown("<br><br><br>", unsafe_allow_html=True) # Espacio para no tapar contenido

# Usamos columnas de Streamlit para hacer los botones funcionales sobre la barra visual de HTML
nav_cols = st.columns(5)

with nav_cols[0]: # INICIO
    if st.button("🏠", key="nav_home", help="Ir a Tiendas"): ir_a('mall')
with nav_cols[1]: # COMPARTIR
    st.button("🔗", key="nav_share", help="Compartir")
with nav_cols[2]: # VOLUMEN (+)
    st.button("🔊", key="nav_vol", help="Activar Sonido")
with nav_cols[3]: # LUPA
    st.button("🔍", key="nav_search", help="Buscar")
with nav_cols[4]: # ME GUSTA
    st.button("❤️", key="nav_like", help="Me gusta")

# La barra visual estética (TikTok Style)
st.markdown("""
    <div class="nav-bar">
        <div class="nav-item"><div class="nav-icon"></div>Inicio</div>
        <div class="nav-item"><div class="nav-icon"></div>Compartir</div>
        <div class="nav-item"><div class="plus-btn">+</div></div>
        <div class="nav-item"><div class="nav-icon"></div>Buscar</div>
        <div class="nav-item"><div class="nav-icon"></div>Perfil</div>
    </div>
    """, unsafe_allow_html=True)