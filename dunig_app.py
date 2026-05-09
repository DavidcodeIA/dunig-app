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
# 2. ESTÉTICA INMERSIVA FULL SCREEN (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    header {visibility: hidden;} 
    
    /* Contenedor Full Screen Cuadrado */
    .tiktok-container {
        position: relative;
        width: 100%;
        height: 90vh; /* Máximo alto de pantalla */
        overflow: hidden;
        background: #000;
        margin-bottom: 0px;
        border-radius: 0px !important; 
        border: none !important;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Burbuja Flotante de Regreso Única */
    .back-bubble {
        position: absolute;
        top: 20px;
        left: 20px;
        z-index: 100;
        background: rgba(0, 0, 0, 0.5);
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(10px);
        cursor: pointer;
        text-decoration: none;
    }

    /* Overlay de Info Inferior */
    .info-overlay {
        position: absolute;
        bottom: 30px;
        left: 20px;
        z-index: 10;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
        pointer-events: none;
    }

    .user-handle { font-weight: 800; font-size: 1.4rem; color: #D4AF37; margin-bottom: 10px; }
    
    .price-tag {
        background: rgba(0, 0, 0, 0.6);
        color: #39FF14;
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.4rem;
        border: 2px solid #39FF14;
        display: inline-block;
    }

    /* Botón de compra Cuadrado Full Width */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important; 
        font-weight: 900 !important;
        height: 70px !important;
        border: none !important;
        width: 100% !important;
        font-size: 1.3rem !important;
        margin-top: -5px;
    }

    /* Eliminar paddings extra de Streamlit */
    [data-testid="stVerticalBlock"] > div { padding: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DE COMPRA
# ==========================================
@st.dialog("💎 PROCESAR PEDIDO")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **PAGO:** {tienda.get('datos_pago', 'Consultar')}")
    
    if st.button("🚀 CONFIRMAR POR WHATSAPP"):
        msj = f"💎 *PEDIDO D'UNIG*\n📦 *Producto:* {producto['nombre_producto']}\n💰 *Total:* ${total}"
        tel = str(tienda['whatsapp']).replace("+", "").strip()
        st.link_button("IR A WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. VISTAS
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
        # VIDEO PANTALLA COMPLETA CON BURBUJA DE VOLVER
        st.markdown(f"""
            <div class="tiktok-container">
                <a href="javascript:window.location.reload();" class="back-bubble" onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'back'}}, '*')">
                    ⬅
                </a>
                <video class="tiktok-video" autoplay loop muted playsinline controls>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                <div class="info-overlay">
                    <div class="user-handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div class="price-tag">${p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón invisible funcional para el cambio de estado
        if st.button("ATRÁS", key=f"logic_back_{idx}", icon="🔙"):
            ir_a('mall')

        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            ventana_pago(p, t)
            
        st.markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)