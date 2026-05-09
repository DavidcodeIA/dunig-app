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
    div[data-testid="stVerticalBlock"] > div:has(div.tiktok-container) {
        padding: 0px;
        margin-bottom: -1rem;
    }

    /* Contenedor principal de Video */
    .tiktok-container {
        position: relative;
        width: 100%;
        height: 85vh; /* Altura casi total de pantalla */
        border-radius: 25px;
        overflow: hidden;
        background: #000;
        margin-bottom: 10px;
        border: 1px solid #333;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Clave para el estilo TikTok */
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

    .user-handle { font-weight: 800; font-size: 1.2rem; color: #D4AF37; margin-bottom: 5px; }
    .product-title { font-size: 1rem; opacity: 0.9; margin-bottom: 10px; }
    
    /* Burbuja de Precio Neón dentro del video */
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

    /* Botón de compra estilizado */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 50px !important;
        font-weight: 800 !important;
        height: 55px !important;
        border: none !important;
    }
    
    /* Imágenes del Mall */
    .mall-card {
        width: 100%; aspect-ratio: 1/1; object-fit: cover; border-radius: 20px;
        border: 2px solid #D4AF37; margin-bottom: 5px;
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
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG MALL</h1>", unsafe_allow_html=True)
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

# --- VISTA: TIENDA (ESTILO TIKTOK SCREENSHOT) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    c1, c2 = st.columns([1, 5])
    with c1: 
        if st.button("⬅️"): ir_a('mall')
    with c2:
        st.markdown(f"<h3 style='color:#D4AF37; margin:0;'>{t['nombre_comercio']}</h3>", unsafe_allow_html=True)

    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        # Estructura visual idéntica a tu captura
        st.markdown(f"""
            <div class="tiktok-container">
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
        
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            ventana_pago(p, t)
        st.markdown("<br><br>", unsafe_allow_html=True)

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
        # Aquí iría el resto de tu lógica de carga de productos (t1, t2, t3)
        st.success(f"Sesión activa: {st.session_state.user_email}")
        if st.button("CERRAR SESIÓN"):
            st.session_state.logged_in = False
            st.rerun()