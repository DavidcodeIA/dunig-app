import streamlit as st
from supabase import create_client
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="wide", 
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
# 2. ESTÉTICA "FULL SCREEN" SIN MÁRGENES (CSS)
# ==========================================
st.markdown("""
    <style>
    /* ELIMINAR ESPACIO SUPERIOR Y MÁRGENES DE STREAMLIT */
    .main { background-color: #000000 !important; }
    header { visibility: hidden; height: 0px; } 
    footer { visibility: hidden; }
    
    /* Forzar que el contenedor no tenga padding arriba */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }

    [data-testid="stVerticalBlock"] {
        scroll-snap-type: y mandatory;
        overflow-y: scroll;
        height: 100vh;
        gap: 0rem !important;
    }

    /* Secciones de video */
    .snap-section {
        scroll-snap-align: start;
        scroll-snap-stop: always;
        position: relative;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: #000;
        margin-top: 0px !important;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Interfaz Flotante */
    .floating-ui {
        position: absolute;
        bottom: 100px;
        left: 20px;
        z-index: 100;
        pointer-events: none;
    }

    .user-handle { 
        font-weight: 800; 
        font-size: 1.8rem; 
        color: #D4AF37; 
        text-shadow: 2px 2px 10px rgba(0,0,0,1);
    }

    .price-burbuja {
        background: rgba(0, 0, 0, 0.7);
        color: #39FF14;
        padding: 10px 25px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.6rem;
        border: 2px solid #39FF14;
        display: inline-block;
        margin-top: 10px;
    }

    /* Botón ATRÁS corregido y visible */
    div.stButton > button[key^="back_"] {
        position: fixed;
        top: 15px !important; /* Pegado arriba */
        left: 15px !important;
        z-index: 9999 !important;
        background: rgba(0, 0, 0, 0.6) !important;
        color: #FF5F1F !important; 
        border: 2px solid #FF5F1F !important;
        border-radius: 50px !important;
        font-weight: 900 !important;
        height: 40px !important;
        padding: 0px 15px !important;
    }

    /* Botón COMPRAR corregido y visible */
    div.stButton > button[key^="buy_"] {
        position: fixed;
        bottom: 0px !important;
        left: 0px !important;
        z-index: 9998 !important;
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important; 
        font-weight: 900 !important;
        height: 65px !important;
        border: none !important;
        width: 100% !important;
    }

    ::-webkit-scrollbar { display: none; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE PAGO
# ==========================================
@st.dialog("💎 PROCESAR PEDIDO")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **MÉTODO DE PAGO:**\n{tienda.get('datos_pago', 'Acordar con el vendedor')}")
    ref = st.text_input("Referencia de Pago")
    
    if st.button("🚀 ENVIAR PEDIDO", key="final_confirm"):
        if ref:
            msj = f"💎 *NUEVO PEDIDO D'UNIG*\n📦 *Producto:* {producto['nombre_producto']}\n🔢 *Cantidad:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("FINALIZAR EN WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else:
            st.error("Por favor, ingresa la referencia de pago.")

# ==========================================
# 4. VISTAS
# ==========================================
if st.session_state.view == 'mall':
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
    
    # Botón Atrás Fijo
    if st.button("⬅ ATRÁS", key="back_fixed"):
        ir_a('mall')

    for idx, p in enumerate(prods):
        # Eliminado el "muted" para que intente sonar solo
        st.markdown(f"""
            <div class="snap-section">
                <video class="tiktok-video" autoplay loop playsinline>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                <div class="floating-ui">
                    <div class="user-handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div class="price-burbuja">${p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}"):
            ventana_pago(p, t)