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
# 2. ESTÉTICA INMERSIVA TOTAL (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Fondo negro y eliminación de márgenes de Streamlit */
    .main { background-color: #000000 !important; }
    header { visibility: hidden; }
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }

    /* Contenedor de Video: Cuadrado y Pantalla Completa */
    .tiktok-container-full {
        position: relative;
        width: 100vw;
        height: 88vh; /* Ocupa la mayor parte del alto visual */
        background: #000;
        overflow: hidden;
        border: none !important;
        border-radius: 0px !important; /* Esquinas cuadradas */
    }

    .tiktok-video-full {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Asegura que cubra todo el contenedor */
    }

    /* Burbuja Flotante para Volver */
    .back-bubble {
        position: absolute;
        top: 20px;
        left: 20px;
        z-index: 100;
        background: rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(10px);
        color: white;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        border: 1px solid rgba(255,255,255,0.2);
        cursor: pointer;
        text-decoration: none;
    }

    /* Overlay de Información Inferior */
    .info-overlay {
        position: absolute;
        bottom: 40px;
        left: 20px;
        z-index: 10;
        pointer-events: none;
    }

    .user-handle { 
        font-weight: 800; 
        font-size: 1.3rem; 
        color: #D4AF37; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        margin-bottom: 10px;
    }

    .price-tag-luxury {
        background: rgba(0, 0, 0, 0.6);
        color: #39FF14;
        padding: 6px 18px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.4rem;
        border: 2px solid #39FF14;
        display: inline-block;
        backdrop-filter: blur(5px);
    }

    /* Botón de Compra Luxury Cuadrado */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important;
        font-weight: 800 !important;
        height: 65px !important;
        border: none !important;
        width: 100% !important;
        font-size: 1.2rem !important;
        text-transform: uppercase;
    }
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
    st.info(f"💳 **PAGO:** {tienda.get('datos_pago', 'Consultar con vendedor')}")
    ref = st.text_input("Referencia de Pago")
    
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"💎 *PEDIDO D'UNIG*\n📦 {producto['nombre_producto']}\n💰 Total: ${total}\n🎫 Ref: {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("ENVIAR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. SISTEMA DE VISTAS
# ==========================================

# --- VISTA: MALL ---
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

# --- VISTA: TIENDA (PANTALLA COMPLETA) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for idx, p in enumerate(prods):
        # El botón de "Volver" ahora es una burbuja HTML que recarga para ir al Mall
        st.markdown(f"""
            <div class="tiktok-container-full">
                <a href="javascript:window.location.reload();" class="back-bubble" onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'back'}}, '*')">
                    ⬅
                </a>
                
                <video class="tiktok-video-full" autoplay loop muted playsinline controls>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>

                <div class="info-overlay">
                    <div class="user-handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div class="price-tag-luxury">${p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón invisible/funcional de Streamlit para captar el regreso
        if st.button("VOLVER AL MALL", key=f"back_logic_{idx}"):
            ir_a('mall')

        # Botón de Compra
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}"):
            ventana_pago(p, t)
            
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)