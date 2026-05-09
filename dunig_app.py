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
# 2. ESTÉTICA ULTRA-INMERSIVA (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Fondo negro y eliminación de márgenes nativos de Streamlit */
    .main { background-color: #000000 !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    
    /* Contenedor TikTok Pantalla Completa (Sin bordes ovalados) */
    .tiktok-full-container {
        position: relative;
        width: 100vw; /* Ancho total de la ventana */
        height: 90vh; /* Altura inmersiva */
        background: #000;
        margin-bottom: 5px;
        overflow: hidden;
    }

    .tiktok-video-full {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Info Superpuesta */
    .info-overlay {
        position: absolute;
        bottom: 40px;
        left: 20px;
        z-index: 10;
        color: white;
        text-shadow: 2px 2px 8px rgba(0,0,0,1);
        pointer-events: none;
    }

    .user-handle { font-weight: 800; font-size: 1.4rem; color: #D4AF37; margin-bottom: 2px; }
    .product-title { font-size: 1.1rem; opacity: 0.9; margin-bottom: 12px; }
    
    .price-tag {
        background: rgba(0, 0, 0, 0.7);
        color: #39FF14;
        padding: 6px 18px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.4rem;
        border: 2px solid #39FF14;
        display: inline-block;
    }

    /* Botón ATRÁS Estático (Fixed) */
    .st-emotion-cache-12fmueu { display: none; } /* Ocultar cabecera default */
    
    .fixed-back {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 1000;
    }

    /* Estilo del Botón de Compra */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important; /* Cuadrado para match con video */
        font-weight: 800 !important;
        height: 60px !important;
        border: none !important;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS
# ==========================================
@st.dialog("💎 DETALLES DEL PEDIDO")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **PAGO:** {tienda.get('datos_pago', 'Consultar')}")
    ref = st.text_input("Referencia de Pago")
    if st.button("🚀 CONFIRMAR"):
        if ref:
            msj = f"💎 *PEDIDO*\n📦 {producto['nombre_producto']}\n🔢 Cant: {cantidad}\n💰 Total: ${total}\n🎫 Ref: {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("ENVIAR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================

# --- VISTA: MALL ---
if st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37; padding-top:20px;'>🏙️ D'UNIG MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
    
    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(tiendas):
                t = tiendas[i + j]
                with cols[j]:
                    st.image(t.get("portada_url", ""), use_container_width=True)
                    if st.button(f"{t['nombre_comercio']}", key=f"t_{t['id']}", use_container_width=True):
                        st.session_state.tienda_actual = t
                        ir_a('tienda')

# --- VISTA: TIENDA (FULL SCREEN TIKTOK) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    
    # Botón Atrás Estático
    st.markdown('<div class="fixed-back">', unsafe_allow_html=True)
    if st.button("⬅️", key="static_back"):
        ir_a('mall')
    st.markdown('</div>', unsafe_allow_html=True)

    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        # Contenedor de Video Sin Esquinas y Ancho Total
        st.markdown(f"""
            <div class="tiktok-full-container">
                <video class="tiktok-video-full" autoplay loop muted playsinline>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                <div class="info-overlay">
                    <div class="user-handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div class="product-title">{p['nombre_producto']}</div>
                    <div class="price-tag">${p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón de compra pegado al video
        if st.button(f"🛒 COMPRAR {p['nombre_producto'].upper()}", key=f"buy_{p['id']}", use_container_width=True):
            ventana_pago(p, t)
        
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)