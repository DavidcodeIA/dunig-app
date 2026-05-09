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
        return None

supabase = init_connection()

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA 9:16 FULL SCREEN (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    header {visibility: hidden; height: 0px;} 
    footer {visibility: hidden;}
    
    [data-testid="stAppViewBlockContainer"] {
        padding: 0rem !important;
        max-width: 100% !important;
    }

    /* EFECTO IMÁN */
    [data-testid="stVerticalBlock"] {
        scroll-snap-type: y mandatory;
        overflow-y: scroll;
        height: 100vh;
        gap: 0rem !important;
    }

    .video-container-916 {
        scroll-snap-align: start;
        scroll-snap-stop: always;
        position: relative;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: #000;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .info-overlay {
        position: absolute;
        bottom: 30px;
        left: 20px;
        z-index: 10;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
        pointer-events: none;
    }

    .user-handle { font-weight: 800; font-size: 1.6rem; color: #D4AF37; margin-bottom: 5px; }
    
    .price-tag {
        background: rgba(0, 0, 0, 0.6);
        color: #39FF14;
        padding: 8px 25px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.5rem;
        border: 2px solid #39FF14;
        display: inline-block;
    }

    /* BOTÓN COMPRAR (DORADO) */
    div.stButton > button[key^="buy_"] {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        color: #000 !important; 
        border-radius: 0px !important; 
        font-weight: 900 !important;
        height: 70px !important;
        border: none !important;
        width: 100% !important;
        font-size: 1.3rem !important;
        margin-bottom: 0px !important;
    }

    /* BOTÓN ATRÁS (AZUL MARINO DELGADO) */
    div.stButton > button[key^="back_"] {
        background-color: #001F3F !important; /* Azul Marino */
        color: #FFFFFF !important; 
        border-radius: 0px !important; 
        font-weight: 600 !important;
        height: 40px !important; /* Más delgado */
        border: none !important;
        width: 100% !important;
        font-size: 1rem !important;
        margin-top: 0px !important;
        border-top: 1px solid rgba(255,255,255,0.1) !important;
    }

    ::-webkit-scrollbar { display: none; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. CARRITO DE COMPRAS
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
    
    for idx, p in enumerate(prods):
        # El Video
        st.markdown(f"""
            <div class="video-container-916">
                <video class="tiktok-video" autoplay loop muted playsinline>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                <div class="info-overlay">
                    <div class="user-handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div class="price-tag">${p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # 1. BOTÓN COMPRAR (DORADO)
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            ventana_pago(p, t)
        
        # 2. BOTÓN ATRÁS (AZUL MARINO - DE ÚLTIMO)
        if st.button("VOLVER AL MALL", key=f"back_{idx}"):
            ir_a('mall')
        
        # Espacio mínimo entre bloques de video para el snap
        st.markdown("<div style='height:0px;'></div>", unsafe_allow_html=True)