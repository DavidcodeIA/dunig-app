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
        # Asegúrate de tener estas credenciales en tu archivo .streamlit/secrets.toml
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

supabase = init_connection()

# Inicialización de estados de sesión
if 'view' not in st.session_state: 
    st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: 
    st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA DE PANTALLA COMPLETA (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Fondo negro y eliminación de márgenes de Streamlit */
    .main { background-color: #000000 !important; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    header { visibility: hidden; } /* Oculta la barra superior de Streamlit */
    
    /* Contenedor tipo TikTok: Ocupa el 88% de la altura de la pantalla */
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

    /* Info Superpuesta (Abajo Izquierda) */
    .info-overlay {
        position: absolute;
        bottom: 30px;
        left: 20px;
        z-index: 10;
        color: white;
        text-shadow: 2px 2px 8px rgba(0,0,0,1);
        pointer-events: none; /* Permite que los clics pasen al video si es necesario */
    }

    .user-handle { 
        font-weight: 800; 
        font-size: 1.4rem; 
        color: #D4AF37; 
        margin-bottom: 5px; 
    }
    
    .product-title { 
        font-size: 1rem; 
        opacity: 0.9; 
        margin-bottom: 10px; 
    }
    
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

    /* Estilo del Botón de Compra y Botón Atrás (Dorado Luxury) */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important;
        font-weight: 800 !important;
        height: 55px !important;
        border: none !important;
        width: 100% !important;
        transition: 0.3s;
    }
    
    .stButton>button:active {
        transform: scale(0.98);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS (FORMULARIO DE PEDIDO)
# ==========================================
@st.dialog("💎 PROCESAR PEDIDO")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    
    # Cálculo de precio
    precio_num = float(producto['precio'])
    total = precio_num * cantidad
    
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    
    st.info(f"💳 **MÉTODO DE PAGO:** {tienda.get('datos_pago', 'Consultar por WhatsApp')}")
    ref = st.text_input("Número de Referencia de Pago")
    
    if st.button("🚀 CONFIRMAR Y ENVIAR"):
        if ref:
            msj = (f"💎 *NUEVO PEDIDO D'UNIG*\n"
                   f"📦 *Producto:* {producto['nombre_producto']}\n"
                   f"🔢 *Cantidad:* {cantidad}\n"
                   f"💰 *Total:* ${total:,.2f}\n"
                   f"🎫 *Referencia:* {ref}")
            
            # Limpiar el número de teléfono
            tel = str(tienda['whatsapp']).replace("+", "").replace(" ", "").strip()
            url_wa = f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}"
            
            st.success("¡Pedido generado! Redirigiendo a WhatsApp...")
            st.link_button("ABRIR WHATSAPP", url_wa)
        else:
            st.warning("Por favor, ingresa la referencia del pago.")

# ==========================================
# 4. LÓGICA DE VISTAS (NAVEGACIÓN)
# ==========================================

# --- VISTA: MALL (LISTADO DE TIENDAS) ---
if st.session_state.view == 'mall':
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    
    # Obtener tiendas activas de Supabase
    tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
    
    if tiendas:
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        # Mostrar imagen de portada de la tienda
                        st.image(t.get("portada_url", "https://via.placeholder.com/400x400"), use_container_width=True)
                        if st.button(f"{t['nombre_comercio'].upper()}", key=f"t_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')
    else:
        st.write("Cargando tiendas o no hay tiendas disponibles...")

# --- VISTA: TIENDA (SCROLL DE VIDEOS CON AUDIO) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    
    # Obtener productos de la tienda actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    # Aviso de audio (los navegadores requieren interacción para el sonido)
    st.toast("Toca la pantalla para activar el audio 🔊")

    if prods:
        for idx, p in enumerate(prods):
            # Contenedor del Video (Sin el atributo 'muted' para que se escuche)
            st.markdown(f"""
                <div class="tiktok-full-container">
                    <video class="tiktok-video-full" autoplay loop playsinline>
                        <source src="{p['video_url']}" type="video/mp4">
                        Tu navegador no soporta videos.
                    </video>
                    <div class="info-overlay">
                        <div class="user-handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                        <div class="product-title">{p['nombre_producto']}</div>
                        <div class="price-tag">${p['precio']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Botones de Acción (Compra y Regreso)
            col_buy, col_back = st.columns([4, 1])
            with col_buy:
                if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
                    ventana_pago(p, t)
            with col_back:
                if st.button("⬅️", key=f"back_{idx}", use_container_width=True):
                    ir_a('mall')
            
            # Espaciador entre videos
            st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    else:
        st.warning("Esta tienda aún no tiene productos.")
        if st.button("VOLVER AL MALL"):
            ir_a('mall')