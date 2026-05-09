import streamlit as st
from supabase import create_client, Client
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
# 2. ESTÉTICA TOTALMENTE EXPANDIDA (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    header {visibility: hidden;} 
    
    /* Expansión total: elimina márgenes superiores y laterales */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }

    .tiktok-container {
        position: relative;
        width: 100%;
        height: 85vh; 
        overflow: hidden;
        background: #000;
        margin: 0px;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Info Overlay Inferior */
    .info-overlay {
        position: absolute;
        bottom: 30px;
        left: 20px;
        z-index: 10;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
        pointer-events: none;
    }

    .user-handle { font-weight: 800; font-size: 1.5rem; color: #D4AF37; margin-bottom: 5px; }
    
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

    /* Botón de compra y atrás Luxury */
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
    }

    /* Botón Atrás específico (más sobrio) */
    div.stButton > button[key^="back_"] {
        background: #1A1A1A !important;
        color: #D4AF37 !important;
        border: 1px solid #D4AF37 !important;
    }

    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DEL CARRITO (DIÁLOGO)
# ==========================================
@st.dialog("🛒 TU PEDIDO LUXURY")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("¿Cuántas unidades deseas?", min_value=1, value=1)
    
    # Cálculo dinámico
    precio_unidad = float(producto['precio'])
    total = precio_unidad * cantidad
    
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.markdown(f"**Comercio:** {tienda['nombre_comercio']}")
    st.info(f"💳 **Método de Pago:** {tienda.get('datos_pago', 'Acordar con el vendedor')}")
    
    if st.button("🚀 FINALIZAR PEDIDO (WHATSAPP)", use_container_width=True):
        msj = f"✨ *NUEVO PEDIDO D'UNIG*\n\n🛍️ *Producto:* {producto['nombre_producto']}\n🔢 *Cantidad:* {cantidad}\n💰 *Total:* ${total:,.2f}\n\n📍 *Tienda:* {tienda['nombre_comercio']}"
        tel = str(tienda['whatsapp']).replace("+", "").strip()
        link_wa = f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}"
        st.link_button("ABRIR WHATSAPP", link_wa, use_container_width=True)

# ==========================================
# 4. VISTAS
# ==========================================
if st.session_state.view == 'mall':
    # Títulos eliminados para expansión máxima
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
        # Video sin títulos estorbando arriba
        st.markdown(f"""
            <div class="tiktok-container">
                <video class="tiktok-video" autoplay loop muted playsinline controls>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                <div class="info-overlay">
                    <div class="user-handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div class="price-tag">${p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botones integrados debajo del video
        col_back, col_buy = st.columns([1, 2])
        
        with col_back:
            if st.button("ATRÁS", key=f"back_{idx}", use_container_width=True):
                ir_a('mall')
        
        with col_buy:
            if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            
        st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)