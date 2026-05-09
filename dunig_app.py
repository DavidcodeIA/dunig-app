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
# 2. ESTÉTICA "SIDE-ACTIONS" (CSS)
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
        height: 92vh; 
        background: #000;
        overflow: hidden;
    }

    .video-bg {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* BARRA LATERAL FLOTANTE (DENTRO DEL VIDEO) */
    .side-actions {
        position: absolute;
        right: 15px;
        bottom: 120px;
        display: flex;
        flex-direction: column;
        gap: 20px;
        align-items: center;
        z-index: 100;
    }

    .action-button-ui {
        width: 45px;
        height: 45px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        color: white;
        font-size: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* INFO DEL PRODUCTO (IZQUIERDA) */
    .product-info {
        position: absolute;
        bottom: 30px;
        left: 20px;
        z-index: 10;
        color: white;
        text-shadow: 2px 2px 8px rgba(0,0,0,1);
        max-width: 70%;
    }

    .shop-name { font-weight: 800; font-size: 1.3rem; color: #D4AF37; margin-bottom: 5px; }
    .price-tag { 
        color: #39FF14; font-weight: 900; font-size: 1.5rem; 
        border: 2px solid #39FF14; padding: 4px 15px; border-radius: 50px;
        background: rgba(0,0,0,0.6); display: inline-block; margin-top: 10px;
    }

    /* BOTÓN COMPRAR (PEGADO AL FINAL DEL VIDEO) */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important;
        font-weight: 900 !important;
        height: 60px !important;
        border: none !important;
        width: 100% !important;
        font-size: 1.2rem !important;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS
# ==========================================
@st.dialog("💎 PROCESAR ADQUISICIÓN")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad deseada", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("VALOR TOTAL", f"${total:,.2f}")
    st.divider()
    ref = st.text_input("Ingrese Referencia de Pago")
    if st.button("🚀 ENVIAR PEDIDO AHORA"):
        if ref:
            msj = f"💎 *NUEVO PEDIDO D'UNIG*\n📦 *Item:* {producto['nombre_producto']}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("COMPLETAR EN WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. LÓGICA DE NAVEGACIÓN
# ==========================================

# --- VISTA: MALL ---
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

# --- VISTA: TIENDA (FULL VIDEO + SIDE ACTIONS) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for idx, p in enumerate(prods):
        # Contenedor Visual del Video e Iconos
        st.markdown(f"""
            <div class="video-container">
                <video class="video-bg" autoplay loop muted playsinline>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                
                <!-- Iconos Laterales Estilo TikTok -->
                <div class="side-actions">
                    <div class="action-button-ui">🏠</div>
                    <div class="action-button-ui">❤️</div>
                    <div class="action-button-ui">🔗</div>
                    <div class="action-button-ui">🔊</div>
                    <div class="action-button-ui">🔍</div>
                </div>

                <!-- Información del Producto -->
                <div class="product-info">
                    <div class="shop-name">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div style="font-size: 1.1rem; opacity: 0.9;">{p['nombre_producto']}</div>
                    <div class="price-tag">${p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botones invisibles de Streamlit colocados estratégicamente para dar funcionalidad
        # (Se usan columnas para alinear los botones sobre los iconos laterales)
        col_space, col_btns = st.columns([8, 1])
        with col_btns:
            # Botón invisible para "Inicio" (Regresa al Mall)
            if st.button("🏠", key=f"btn_home_{idx}", help="Regresar al Mall"): 
                ir_a('mall')
            st.button("❤️", key=f"btn_like_{idx}")
            st.button("🔗", key=f"btn_share_{idx}")
            st.button("🔊", key=f"btn_vol_{idx}")
            st.button("🔍", key=f"btn_search_{idx}")

        # Botón de Compra Luxury
        if st.button(f"🛍️ ADQUIRIR ESTE PRODUCTO", key=f"buy_{p['id']}", use_container_width=True):
            ventana_pago(p, t)
        
        st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)