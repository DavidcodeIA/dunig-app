import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import time
from datetime import datetime, date

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

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

# Estado de la Sesión
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS ESTILO TIKTOK)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000000; color: #ffffff; }
    
    /* Contenedor estilo TikTok */
    .tiktok-container {
        position: relative;
        width: 100%;
        height: 80vh; /* Altura inmersiva */
        border-radius: 30px;
        overflow: hidden;
        margin-bottom: 20px;
        border: 2px solid #D4AF37;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover; /* Hace que el video llene todo el espacio */
    }

    .price-bubble {
        position: absolute;
        top: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.7);
        color: #39FF14;
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.5rem;
        border: 2px solid #39FF14;
        z-index: 10;
    }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; 
        border-radius: 50px !important;
        font-weight: 800 !important;
        height: 60px !important;
        font-size: 1.1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS (CARRITO)
# ==========================================
@st.dialog("💎 CARRITO D'UNIG LUXURY")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **DATOS DE PAGO:**\n{tienda.get('datos_pago', 'Consultar al vendedor')}")
    ref = st.text_input("Ingrese Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Producto:* {producto['nombre_producto']}\n🔢 *Cant:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("ENVIAR POR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else:
            st.error("Por favor, ingrese la referencia de pago")

# ==========================================
# 4. VISTAS
# ==========================================
es_admin_master = st.query_params.get("admin") == "true"

# --- VISTA: MALL ---
if not es_admin_master and st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
    
    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(tiendas):
                t = tiendas[i + j]
                with cols[j]:
                    url = t.get("portada_url", "")
                    if url.lower().endswith(('.mp4', '.mov')):
                        st.markdown(f'<video autoplay loop muted playsinline style="width:100%; aspect-ratio:1/1; object-fit:cover; border-radius:20px; border:1px solid #D4AF37;"><source src="{url}"></video>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<img src="{url}" style="width:100%; aspect-ratio:1/1; object-fit:cover; border-radius:20px; border:1px solid #D4AF37;">', unsafe_allow_html=True)
                    
                    if st.button(f"{t['nombre_comercio'].upper()}", key=f"m_{t['id']}", use_container_width=True):
                        st.session_state.tienda_actual = t
                        ir_a('tienda')

# --- VISTA: TIENDA (ESTILO TIKTOK) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        # El contenedor TikTok con precio flotante y video a pantalla completa
        st.markdown(f"""
            <div class="tiktok-container">
                <div class="price-bubble">${p['precio']}</div>
                <video class="tiktok-video" autoplay loop muted playsinline controls>
                    <source src="{p['video_url']}" type="video/mp4">
                </video>
            </div>
        """, unsafe_allow_html=True)
        
        # Botón de compra llamativo debajo de cada video
        if st.button(f"🛒 PEDIR {p['nombre_producto'].upper()}", key=f"buy_{p['id']}", use_container_width=True):
            ventana_pago(p, t)
        
        st.markdown("<br><br>", unsafe_allow_html=True) # Espacio entre videos

# --- LOGIN / PANEL (Simplificado para el ejemplo) ---
else:
    st.info("Panel de Control Activo")