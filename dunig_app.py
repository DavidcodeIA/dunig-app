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
# 2. ESTÉTICA TIKTOK INMERSIVA (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    
    /* Contenedor Cuadrado y Full */
    .tiktok-container {
        position: relative;
        width: 100%;
        height: 88vh; 
        background: #000;
        margin-bottom: 0px;
        overflow: hidden;
        /* Esquinas cuadradas */
        border-radius: 0px !important;
        border: none !important;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Overlay Minimalista */
    .info-overlay {
        position: absolute;
        bottom: 40px;
        left: 20px;
        z-index: 10;
        pointer-events: none;
    }

    .user-handle { 
        font-weight: 800; 
        font-size: 1.4rem; 
        color: #D4AF37; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        margin-bottom: 15px;
    }

    /* Contenedor de Burbujas Inferiores */
    .burbujas-container {
        display: flex;
        align-items: center;
        gap: 12px;
        pointer-events: auto; /* Para que el botón de atrás funcione */
    }

    .price-tag {
        background: rgba(0, 0, 0, 0.6);
        color: #39FF14;
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.4rem;
        border: 2px solid #39FF14;
        backdrop-filter: blur(5px);
    }

    /* Botón Atrás Flotante Estilo Burbuja */
    .back-float {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        border: 1px solid rgba(255,255,255,0.4);
        backdrop-filter: blur(10px);
        cursor: pointer;
        text-decoration: none;
    }

    /* Botón Compra Luxury */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important; /* Cuadrado también */
        font-weight: 800 !important;
        height: 60px !important;
        border: none !important;
        width: 100% !important;
        font-size: 1.1rem !important;
    }

    /* Eliminar espacios de Streamlit */
    header {visibility: hidden;}
    [data-testid="stVerticalBlock"] { gap: 0rem !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DE COMPRA
# ==========================================
@st.dialog("💎 PROCESAR PEDIDO")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ Confirmar Pedido")
    st.write(f"Producto: **{producto['nombre_producto']}**")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **MÉTODO:** {tienda.get('datos_pago', 'Consultar')}")
    ref = st.text_input("Referencia de Pago")
    
    if st.button("🚀 FINALIZAR POR WHATSAPP"):
        if ref:
            msj = f"💎 *NUEVO PEDIDO*\n📦 {producto['nombre_producto']}\n💰 Total: ${total}\n🎫 Ref: {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("ABRIR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. NAVEGACIÓN
# ==========================================

# --- VISTA: MALL ---
if st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37; padding:15px;'>🏙️ D'UNIG MALL</h1>", unsafe_allow_html=True)
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

# --- VISTA: TIENDA INMERSIVA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for idx, p in enumerate(prods):
        # VIDEO CUADRADO SIN TÍTULOS CON BOTÓN ATRÁS INTEGRADO
        st.markdown(f"""
            <div class="tiktok-container">
                <video class="tiktok-video" autoplay loop muted playsinline controls>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                <div class="info-overlay">
                    <div class="user-handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div class="burbujas-container">
                        <div class="price-tag">${p['precio']}</div>
                        <!-- Botón atrás dentro del video -->
                        <a href="javascript:window.location.reload();" class="back-float" onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'back'}}, '*')">
                            ⬅
                        </a>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # El botón de atrás oculto de Streamlit para que la lógica funcione
        if st.button("VOLVER", key=f"back_{idx}", icon="🔙"):
            ir_a('mall')

        # Botón de Compra
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            ventana_pago(p, t)
            
        st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)