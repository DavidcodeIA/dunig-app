import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONEXIÓN Y CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="centered")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS CORREGIDO: BURBUJA SOBRE EL VIDEO
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; }
    
    .fixed-back {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 2000; /* Super alto para que no lo tape nada */
    }

    /* Contenedor relativo para que la burbuja sepa dónde posicionarse */
    .product-card {
        position: relative;
        width: 100%;
        margin-bottom: 25px;
    }

    .video-container {
        width: 100%;
        border-radius: 30px;
        border: 3px solid #D4AF37;
        overflow: hidden;
        box-shadow: 0 20px 50px rgba(0,0,0,0.9);
        background-color: #000;
    }

    /* BURBUJA FLOTANTE CORREGIDA */
    .price-bubble {
        position: absolute;
        top: 15px;
        right: 15px;
        background: linear-gradient(135deg, #FFD700 0%, #D4AF37 50%, #B8860B 100%);
        color: #000 !important;
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.4rem;
        z-index: 1500; /* Asegura que esté por encima del video */
        border: 2px solid #FFFFFF;
        box-shadow: 0 8px 15px rgba(212, 175, 55, 0.8);
        pointer-events: none; /* Para que no interfiera con el play del video */
    }

    .stButton>button {
        background: linear-gradient(145deg, #D4AF37, #B8860B) !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: 900 !important;
        box-shadow: 0 6px 0 #5d4814 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VENTANA DE PAGO (CORRECCIÓN DE NONE)
# ==========================================
@st.dialog("💎 DETALLES DEL PEDIDO")
def ventana_pago(producto, comercio):
    # Forzar lectura fresca de la base de datos
    res = supabase.table("perfiles_comercio").select("datos_pago, whatsapp, nombre_comercio").eq("id", comercio['id']).single().execute()
    tienda = res.data
    
    st.markdown(f"### 🛍️ {producto['nombre_producto']}")
    st.markdown(f"**Precio:** `${producto['precio']}`")
    st.divider()
    
    st.markdown("### 🏦 Cuentas de Pago")
    
    # CORRECCIÓN DE "NONE": Verificamos si existe el dato
    info_pago = tienda.get('datos_pago')
    if info_pago is None or info_pago.strip() == "":
        st.warning("⚠️ El vendedor aún no ha cargado sus datos de pago en el Panel de Control.")
    else:
        st.info(info_pago)
    
    referencia = st.text_input("Número de Referencia Bancaria")
    
    if st.button("📲 GENERAR TICKET WHATSAPP", use_container_width=True):
        if referencia:
            msj = (
                f"✨ *ORDEN D'UNIG PLATINUM*\n\n"
                f"🛍️ *Producto:* {producto['nombre_producto']}\n"
                f"💰 *Precio:* ${producto['precio']}\n"
                f"🔢 *Referencia:* {referencia}\n"
                f"🏪 *Tienda:* {tienda['nombre_comercio']}\n"
            )
            link = f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}"
            st.link_button("ABRIR WHATSAPP", link)
        else:
            st.error("La referencia es obligatoria.")

# ==========================================
# 4. VISTAS
# ==========================================

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg")
    if st.button("🏠 MALL", use_container_width=True): ir_a('mall')
    if st.button("⚙️ PANEL CONTROL", use_container_width=True): ir_a('admin')

# --- VISTA: TIENDA ---
if st.session_state.view == 'tienda':
    st.markdown('<div class="fixed-back">', unsafe_allow_html=True)
    if st.button("⬅️ VOLVER"): ir_a('mall')
    st.markdown('</div>', unsafe_allow_html=True)
    
    t_act = st.session_state.tienda_actual
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t_act['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t_act['nombre_comercio']).execute()
    
    for p in prods.data:
        # Usamos un div 'product-card' para envolver burbuja + video
        st.markdown(f'''
            <div class="product-card">
                <div class="price-bubble">${p['precio']}</div>
                <div class="video-container">
            ''', unsafe_allow_html=True)
        
        st.video(p['video_url'])
        
        st.markdown('</div></div>', unsafe_allow_html=True) # Cerramos los divs
        
        if st.button(f"🛒 COMPRAR YA: {p['nombre_producto']}", key=f"p_{p['id']}", use_container_width=True):
            ventana_pago(p, t_act)
        st.markdown("<br><br>", unsafe_allow_html=True)

# --- VISTA: MALL ---
elif st.session_state.view == 'mall':
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg", use_container_width=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    for t in tiendas.data:
        if st.button(f"✨ ENTRAR A {t['nombre_comercio'].upper()}", key=t['id'], use_container_width=True):
            st.session_state.tienda_actual = t
            ir_a('tienda')

# --- VISTA: ADMIN ---
elif st.session_state.view == 'admin':
    if st.button("⬅️ VOLVER"): ir_a('mall')
    email = st.text_input("Correo Propietario")
    if email:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email).execute()
        if res.data:
            perf = res.data[0]
            t1, t2, t3 = st.tabs(["📤 SUBIR", "📦 STOCK", "💰 PAGOS"])
            with t3:
                info_bancaria = st.text_area("Cuentas (Banco, Pago Móvil, etc.)", value=perf.get('datos_pago', ''), height=150)
                if st.button("💾 GUARDAR DATOS"):
                    supabase.table("perfiles_comercio").update({"datos_pago": info_bancaria}).eq("id", perf['id']).execute()
                    st.success("¡Datos guardados!")
            # (Resto del código de carga de videos igual...)
