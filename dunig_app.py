import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import time
from datetime import datetime, date

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

# Constantes y Estados
PLANES_LIMITES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA TIKTOK LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Fondo negro total y limpieza de espacios */
    .main { background-color: #000000 !important; }
    header {visibility: hidden;} 
    
    /* Contenedor principal de Video - ESQUINAS CUADRADAS */
    .tiktok-container {
        position: relative;
        width: 100%;
        height: 90vh; 
        overflow: hidden;
        background: #000;
        margin-bottom: 0px;
        border-radius: 0px !important; /* Cuadrado total */
        border: none !important;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Burbuja Flotante para Regresar */
    .back-bubble {
        position: absolute;
        top: 20px;
        left: 20px;
        z-index: 100;
        background: rgba(0, 0, 0, 0.5);
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(10px);
        cursor: pointer;
        text-decoration: none;
    }

    /* Overlay de Información (Abajo Izquierda) */
    .info-overlay {
        position: absolute;
        bottom: 30px;
        left: 20px;
        z-index: 10;
        color: white;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.9);
        pointer-events: none;
    }

    .user-handle { font-weight: 800; font-size: 1.4rem; color: #D4AF37; margin-bottom: 5px; }
    .product-title { font-size: 1.1rem; opacity: 0.9; margin-bottom: 10px; }
    
    /* Burbuja de Precio */
    .price-tag {
        background: rgba(0, 0, 0, 0.6);
        color: #39FF14;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.3rem;
        border: 2px solid #39FF14;
        display: inline-block;
    }

    /* Botón de compra - ESQUINAS CUADRADAS */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 0px !important; /* Cuadrado total */
        font-weight: 800 !important;
        height: 60px !important;
        border: none !important;
        font-size: 1.2rem !important;
    }
    
    /* Imágenes del Mall */
    .mall-card {
        width: 100%; aspect-ratio: 1/1; object-fit: cover; border-radius: 0px;
        border: 1px solid #D4AF37; margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS (CARRITO DE COMPRA)
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
    
    if st.button("🚀 ENVIAR PEDIDO"):
        if ref:
            msj = f"💎 *NUEVO PEDIDO D'UNIG*\n📦 *Producto:* {producto['nombre_producto']}\n🔢 *Cantidad:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("FINALIZAR EN WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else:
            st.error("Ingresa la referencia para validar.")

# ==========================================
# 4. SISTEMA DE NAVEGACIÓN
# ==========================================
es_admin = st.query_params.get("admin") == "true"

# --- VISTA: MALL ---
if not es_admin and st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37; padding:20px;'>🏙️ D'UNIG MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
    
    if not tiendas: st.info("Próximamente más lujo...")
    else:
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.markdown(f'<img src="{t.get("portada_url", "")}" class="mall-card">', unsafe_allow_html=True)
                        if st.button(f"{t['nombre_comercio'].upper()}", key=f"t_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

# --- VISTA: TIENDA (ESTILO INMERSIVO) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for idx, p in enumerate(prods):
        # Contenedor de Video con Burbuja de Regreso y Overlay
        st.markdown(f"""
            <div class="tiktok-container">
                <!-- Burbuja Flotante para volver -->
                <a href="javascript:window.location.reload();" class="back-bubble" onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'back'}}, '*')">
                    ⬅
                </a>
                
                <video class="tiktok-video" autoplay loop muted playsinline controls>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
                
                <div class="info-overlay">
                    <div class="user-handle">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                    <div class="product-title">{p['nombre_producto']}</div>
                    <div class="price-tag">${p['precio']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón de Compra Cuadrado
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            ventana_pago(p, t)
        
        # Botón invisible/funcional para capturar el regreso
        if st.button("VOLVER AL MALL", key=f"back_logic_{idx}"):
            ir_a('mall')
            
        st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)

# --- PANEL DE CONTROL (ADMIN) ---
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL SOCIO</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.container(border=True):
            em = st.text_input("Email").lower().strip()
            cod = st.text_input("Código", type="password").upper().strip()
            if st.button("INGRESAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", em).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == cod:
                    st.session_state.logged_in, st.session_state.user_email = True, em
                    st.rerun()
                else: st.error("Acceso denegado")
    else:
        st.success(f"Sesión activa: {st.session_state.user_email}")
        if st.button("CERRAR SESIÓN"):
            st.session_state.logged_in = False
            st.rerun()