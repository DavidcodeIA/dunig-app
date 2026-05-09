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
# 2. ESTÉTICA Y SCRIPTS (CSS + JS)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    header {visibility: hidden;} 
    
    .tiktok-full-container {
        position: relative;
        width: 100vw;
        height: 88vh;
        background: #000;
        overflow: hidden;
    }

    .tiktok-video-full {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* BURBUJA DE AUDIO FLOTANTE */
    .audio-control {
        position: absolute;
        top: 20px;
        right: 20px;
        z-index: 100;
        background: rgba(0, 0, 0, 0.5);
        color: white;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        border: 1px solid rgba(255,255,255,0.3);
        font-size: 20px;
    }

    .info-overlay {
        position: absolute;
        bottom: 30px;
        left: 20px;
        z-index: 10;
        color: white;
        text-shadow: 2px 2px 8px rgba(0,0,0,1);
        pointer-events: none;
    }

    .user-handle { font-weight: 800; font-size: 1.4rem; color: #D4AF37; margin-bottom: 5px; }
    .product-title { font-size: 1rem; opacity: 0.9; margin-bottom: 10px; }
    
    .price-tag {
        background: rgba(0, 0, 0, 0.7);
        color: #39FF14;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.3rem;
        border: 2px solid #39FF14;
        display: inline-block;
    }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important;
        font-weight: 800 !important;
        height: 55px !important;
        border: none !important;
        width: 100% !important;
    }
    </style>

    <script>
    function toggleAudio(id) {
        const video = document.getElementById(id);
        const allVideos = document.querySelectorAll('video');
        const btn = document.getElementById('btn-' + id);
        
        if (video.muted) {
            // Silenciar todos los demás primero
            allVideos.forEach(v => {
                v.muted = true;
                const otherBtn = document.getElementById('btn-' + v.id);
                if (otherBtn) otherBtn.innerText = '🔇';
            });
            // Activar este
            video.muted = false;
            btn.innerText = '🔊';
        } else {
            video.muted = true;
            btn.innerText = '🔇';
        }
    }
    </script>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS (CARRITO)
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

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for idx, p in enumerate(prods):
        video_id = f"video_{idx}"
        
        # Contenedor del Video con Burbuja de Audio
        st.markdown(f"""
            <div class="tiktok-full-container">
                <video id="{video_id}" class="tiktok-video-full" autoplay loop muted playsinline>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                
                <!-- Botón de Sonido -->
                <div id="btn-{video_id}" class="audio-control" onclick="toggleAudio('{video_id}')">
                    🔇
                </div>

                <div class="info-overlay">
                    <div class="user-handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div class="product-title">{p['nombre_producto']}</div>
                    <div class="price-tag">${p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col_buy, col_back = st.columns([4, 1])
        with col_buy:
            if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
        with col_back:
            if st.button("⬅️", key=f"back_{idx}", use_container_width=True):
                ir_a('mall')
        
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)