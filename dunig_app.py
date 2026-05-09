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
# 2. ESTÉTICA Y LÓGICA (CSS + JS)
# ==========================================
st.markdown("""
    <style>
    /* Fondo y reseteo total */
    .main { background-color: #000000 !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    header {visibility: hidden;} 
    
    /* Contenedor Full Screen Cuadrado */
    .tiktok-full-container {
        position: relative;
        width: 100vw;
        height: 90vh;
        background: #000;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .tiktok-video-full {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Abarca toda la pantalla */
        cursor: pointer;
    }

    /* Botón Play Central */
    .play-overlay {
        position: absolute;
        z-index: 20;
        background: rgba(0, 0, 0, 0.4);
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid white;
        cursor: pointer;
        transition: opacity 0.3s ease;
    }

    /* Capa de Información Inferior */
    .info-overlay {
        position: absolute;
        bottom: 30px;
        left: 20px;
        right: 20px;
        z-index: 10;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    /* Fila de Burbujas Flotantes */
    .floating-controls {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Burbuja de Precio */
    .price-tag {
        background: rgba(0, 0, 0, 0.7);
        color: #39FF14;
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.3rem;
        border: 2px solid #39FF14;
    }

    /* Burbuja de Ir Atrás (Flotante) */
    .back-bubble {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        border: 1px solid rgba(255,255,255,0.4);
        cursor: pointer;
        text-decoration: none;
    }

    .user-handle { font-weight: 800; font-size: 1.4rem; color: #D4AF37; text-shadow: 2px 2px 4px black; }

    /* Botón de Compra Luxury */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important;
        font-weight: 800 !important;
        height: 60px !important;
        border: none !important;
        width: 100% !important;
        font-size: 1.2rem !important;
    }
    </style>

    <script>
    function playVideo(id) {
        const vid = document.getElementById(id);
        const overlay = document.getElementById('overlay-' + id);
        if (vid.paused) {
            vid.play();
            vid.muted = false;
            overlay.style.opacity = '0';
            overlay.style.pointerEvents = 'none';
        } else {
            vid.pause();
            overlay.style.opacity = '1';
            overlay.style.pointerEvents = 'auto';
        }
    }
    </script>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS
# ==========================================
@st.dialog("💎 PROCESAR PEDIDO")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **PAGO:** {tienda.get('datos_pago', 'Consultar')}")
    ref = st.text_input("Referencia de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"💎 *PEDIDO*\n📦 {producto['nombre_producto']}\n🔢 Cant: {cantidad}\n💰 Total: ${total}\n🎫 Ref: {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("ENVIAR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. LÓGICA DE VISTAS
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
        v_id = f"vid_{idx}"
        
        # HTML del Video Full con Botones Flotantes
        st.markdown(f"""
            <div class="tiktok-full-container">
                <!-- Botón Play -->
                <div id="overlay-{v_id}" class="play-overlay" onclick="playVideo('{v_id}')">
                    <span style="color:white; font-size:40px; margin-left:5px;">▶</span>
                </div>
                
                <video id="{v_id}" class="tiktok-video-full" loop playsinline onclick="playVideo('{v_id}')">
                    <source src="{p['video_url']}" type="video/mp4">
                </video>

                <!-- Overlay de Info y Burbujas -->
                <div class="info-overlay">
                    <div class="user-handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div style="color:white; font-size:1.1rem; text-shadow:1px 1px 2px black;">{p['nombre_producto']}</div>
                    
                    <div class="floating-controls">
                        <div class="price-tag">${p['precio']}</div>
                        <!-- Botón Atrás como Burbuja -->
                        <a href="javascript:window.location.reload();" class="back-bubble" onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'back'}}, '*')">
                            ⬅
                        </a>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón Streamlit (Compra)
        if st.button(f"🛒 COMPRAR AHORA - {p['nombre_producto']}", key=f"buy_{p['id']}"):
            ventana_pago(p, t)
        
        # Lógica oculta para captar el clic del botón "Atrás" de HTML
        if st.button("VOLVER AL MALL", key=f"back_btn_{idx}", icon="🏙️"):
            ir_a('mall')
        
        st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)