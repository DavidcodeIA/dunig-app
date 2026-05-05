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
# 2. CSS: BOTÓN ATRÁS FIJO Y ESTILO DORADO
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; }
    
    /* Botón Atrás Fijo en la esquina superior izquierda */
    .fixed-back {
        position: fixed;
        top: 10px;
        left: 10px;
        z-index: 9999;
    }

    .video-wrapper {
        position: relative;
        width: 100%;
        border-radius: 25px;
        border: 3px solid #D4AF37;
        overflow: hidden;
        margin-bottom: 15px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.9);
    }

    .floating-price-gold {
        position: absolute;
        top: 20px;
        right: 20px;
        background: linear-gradient(145deg, #FFD700, #D4AF37);
        color: #000;
        padding: 12px 22px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.4rem;
        z-index: 10;
        border: 2px solid #FFF;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.8);
    }

    .stButton>button {
        background: linear-gradient(145deg, #D4AF37, #B8860B) !important;
        color: white !important;
        border-radius: 15px !important;
        font-weight: bold !important;
        box-shadow: 0 5px 0 #5d4814 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DIALOGO DE PAGO Y WHATSAPP ---
@st.dialog("💎 PROCESAR PEDIDO")
def ventana_pago(producto, comercio):
    # Consultar datos frescos de la tienda para asegurar que salgan los datos de pago
    res = supabase.table("perfiles_comercio").select("datos_pago, whatsapp").eq("id", comercio['id']).single().execute()
    datos_frescos = res.data
    
    st.markdown(f"### 🛍️ {producto['nombre_producto']}")
    st.markdown(f"**Monto:** ${producto['precio']}")
    st.divider()
    st.markdown("### 🏦 Datos de Transferencia")
    st.info(datos_frescos.get('datos_pago', 'Datos no configurados por el dueño.'))
    
    ref = st.text_input("Ingrese Nro. de Referencia de Pago")
    
    if st.button("✅ ENVIAR TICKET POR WHATSAPP"):
        if ref:
            # Crear ticket para WhatsApp
            mensaje = (
                f"✨ *TICKET DE PEDIDO D'UNIG PLATINUM*\n\n"
                f"📦 *Producto:* {producto['nombre_producto']}\n"
                f"💰 *Monto:* ${producto['precio']}\n"
                f"🔢 *Referencia:* {ref}\n"
                f"🏪 *Tienda:* {comercio['nombre_comercio']}\n\n"
                f"Favor verificar mi pedido."
            )
            msg_encoded = urllib.parse.quote(mensaje)
            ws_url = f"https://wa.me/{comercio['whatsapp']}?text={msg_encoded}"
            
            # Registrar pedido en DB
            supabase.table("pedidos").insert({
                "producto": producto['nombre_producto'],
                "precio": producto['precio'],
                "referencia": ref,
                "comercio": comercio['nombre_comercio']
            }).execute()
            
            st.success("Redirigiendo a WhatsApp...")
            st.link_button("ABRIR WHATSAPP", ws_url)
        else:
            st.error("Por favor ingrese la referencia.")

# ==========================================
# 3. NAVEGACIÓN Y SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg")
    if st.button("🏠 MALL PRINCIPAL", use_container_width=True): ir_a('mall')
    if st.button("⚙️ PANEL PROPIETARIO", use_container_width=True): ir_a('admin')

# ==========================================
# 4. VISTAS
# ==========================================

# --- VISTA: MALL ---
if st.session_state.view == 'mall':
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg", use_container_width=True)
    busqueda = st.text_input("🔍 Buscar tiendas...", placeholder="Ej: D'Unig...")
    
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    for t in tiendas.data:
        if busqueda.lower() in t['nombre_comercio'].lower():
            if st.button(f"✨ ENTRAR A {t['nombre_comercio'].upper()}", key=t['id'], use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA: TIENDA (VIDEO FEED) ---
elif st.session_state.view == 'tienda':
    # Botón Atrás FIJO
    st.markdown('<div class="fixed-back">', unsafe_allow_html=True)
    if st.button("⬅️ ATRÁS", key="back_btn"): ir_a('mall')
    st.markdown('</div>', unsafe_allow_html=True)
    
    t = st.session_state.tienda_actual
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    
    for p in prods.data:
        with st.container():
            st.markdown(f'''
                <div class="video-wrapper">
                    <div class="floating-price-gold">${p['precio']}</div>
                </div>
            ''', unsafe_allow_html=True)
            st.video(p['video_url'])
            
            if st.button(f"🛍️ COMPRAR YA: {p['nombre_producto']}", key=f"b_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.markdown("<br><br>", unsafe_allow_html=True)

# --- VISTA: ADMIN ---
elif st.session_state.view == 'admin':
    if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
    st.title("🚀 PANEL DE CONTROL")
    email = st.text_input("Correo de Propietario")
    
    if email:
        perfil = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email).execute()
        if perfil.data:
            com = perfil.data[0]
            tab1, tab2, tab3 = st.tabs(["📤 CARGAR", "📦 STOCK", "💰 PAGOS"])
            
            with tab3:
                st.write("### Configurar Datos de Pago")
                pago_txt = st.text_area("Datos (Bancos, Pago Móvil, etc.)", value=com.get('datos_pago', ''))
                if st.button("💾 GUARDAR DATOS"):
                    supabase.table("perfiles_comercio").update({"datos_pago": pago_txt}).eq("id", com['id']).execute()
                    st.success("¡Datos actualizados!")

            with tab1:
                with st.form("upload", clear_on_submit=True):
                    nom = st.text_input("Producto")
                    pre = st.number_input("Precio", min_value=0.0)
                    vid = st.file_uploader("Video", type=['mp4', 'mov'])
                    if st.form_submit_button("PUBLICAR"):
                        path = f"videos/{com['nombre_comercio']}/{random.randint(100,999)}.mp4"
                        supabase.storage.from_("fotos_productos").upload(path, vid.getvalue())
                        url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                        supabase.table("productos").insert({"nombre_producto": nom, "precio": pre, "video_url": url_v, "comercio_relacionado": com['nombre_comercio']}).execute()
                        st.success("¡Publicado!")
