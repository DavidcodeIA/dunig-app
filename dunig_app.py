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
# 2. ESTÉTICA ULTRA-MINIMALISTA (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    header { visibility: hidden; }
    
    /* Contenedor de Video Full Screen */
    .video-container {
        position: relative;
        width: 100vw;
        height: 90vh; 
        background: #000;
        overflow: hidden;
    }

    .video-bg {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* CONTROL DE VOLUMEN (DENTRO DEL VIDEO) */
    .volume-ctrl {
        position: absolute;
        right: 20px;
        top: 20px;
        z-index: 100;
        background: rgba(0, 0, 0, 0.4);
        padding: 10px;
        border-radius: 50%;
        color: white;
        font-size: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* INFO DEL PRODUCTO (IZQUIERDA INFERIOR) */
    .overlay-info {
        position: absolute;
        bottom: 30px;
        left: 20px;
        z-index: 10;
        color: white;
        text-shadow: 2px 2px 10px rgba(0,0,0,1);
    }

    .biz-name { 
        font-weight: 800; 
        font-size: 1.4rem; 
        color: #D4AF37; /* Dorado D'UNIG */
        margin-bottom: 2px;
    }

    .prod-name {
        font-size: 1rem;
        opacity: 0.9;
        margin-bottom: 12px;
    }

    .price-bubble { 
        color: #39FF14; /* Verde Neón */
        font-weight: 900; 
        font-size: 1.5rem; 
        border: 2px solid #39FF14; 
        padding: 5px 18px; 
        border-radius: 50px;
        background: rgba(0,0,0,0.7); 
        display: inline-block;
    }

    /* BOTÓN COMPRAR (ESTILO BARRA) */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important;
        font-weight: 900 !important;
        height: 65px !important;
        border: none !important;
        width: 100% !important;
        font-size: 1.2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VISTAS
# ==========================================

if st.session_state.view == 'mall':
    # Vista de Tiendas
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
    
    # Botón flotante para volver (Discreto)
    if st.button("⬅ VOLVER AL MALL", key="back_to_mall"):
        ir_a('mall')

    for idx, p in enumerate(prods):
        # El Video con los elementos dentro
        st.markdown(f"""
            <div class="video-container">
                <video class="video-bg" autoplay loop muted playsinline>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                
                <!-- Volumen arriba a la derecha -->
                <div class="volume-ctrl">🔊</div>

                <!-- Info abajo a la izquierda -->
                <div class="overlay-info">
                    <div class="biz-name">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div class="prod-name">{p['nombre_producto']}</div>
                    <div class="price-bubble">${p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # El único botón fuera del video es el de compra
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            # Aquí llamamos a la función de pago (omitida para brevedad, pero igual a la anterior)
            st.toast(f"Procesando pedido de {p['nombre_producto']}...")
        
        st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)