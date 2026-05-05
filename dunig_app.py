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
# 2. CSS: DISEÑO PREMIUM Y BURBUJA FIJA
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; }
    
    .fixed-back {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 2500;
    }

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

    .price-bubble {
        position: absolute;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #FFD700 0%, #D4AF37 50%, #B8860B 100%);
        color: #000 !important;
        padding: 10px 25px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.6rem;
        z-index: 1500;
        border: 2px solid #FFFFFF;
        box-shadow: 0 8px 15px rgba(212, 175, 55, 0.8);
    }

    .stButton>button {
        background: linear-gradient(145deg, #D4AF37, #B8860B) !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: 900 !important;
        box-shadow: 0 6px 0 #5d4814 !important;
        transition: all 0.1s;
    }

    .stButton>button:active {
        transform: translateY(3px);
        box-shadow: 0 2px 0 #5d4814 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DE PAGO EN VIVO
# ==========================================
@st.dialog("💎 DETALLES DE COMPRA")
def ventana_pago(producto, comercio_id):
    # Consulta directa para evitar el "None"
    res = supabase.table("perfiles_comercio").select("*").eq("id", comercio_id).single().execute()
    tienda = res.data
    
    st.markdown(f"### 🛍️ {producto['nombre_producto']}")
    st.markdown(f"**Precio:** `${producto['precio']}`")
    st.divider()
    
    st.markdown("### 🏦 Cuentas de Pago")
    info_pago = tienda.get('datos_pago')
    
    if not info_pago or info_pago == "None" or info_pago.strip() == "":
        st.error("⚠️ El vendedor no ha configurado sus datos de pago.")
    else:
        st.info(info_pago)
    
    ref = st.text_input("Número de Referencia Bancaria")
    
    if st.button("📲 ENVIAR TICKET A WHATSAPP", use_container_width=True):
        if ref:
            msj = (
                f"✨ *PEDIDO PLATINUM*\n\n"
                f"📦 *Producto:* {producto['nombre_producto']}\n"
                f"💰 *Precio:* ${producto['precio']}\n"
                f"🔢 *Referencia:* {ref}\n"
                f"🏪 *Tienda:* {tienda['nombre_comercio']}"
            )
            url_wa = f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}"
            st.link_button("🚀 ABRIR WHATSAPP", url_wa)
        else:
            st.warning("Escriba el número de referencia.")

# ==========================================
# 4. VISTAS PRINCIPALES
# ==========================================

with st.sidebar:
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg")
    if st.button("🏠 MALL", use_container_width=True): ir_a('mall')
    if st.button("⚙️ PANEL CONTROL", use_container_width=True): ir_a('admin')

# --- VISTA: TIENDA ---
if st.session_state.view == 'tienda':
    st.markdown('<div class="fixed-back">', unsafe_allow_html=True)
    if st.button("⬅️ ATRÁS"): ir_a('mall')
    st.markdown('</div>', unsafe_allow_html=True)
    
    t = st.session_state.tienda_actual
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    
    for p in prods.data:
        st.markdown(f'''
            <div class="product-card">
                <div class="price-bubble">${p['precio']}</div>
                <div class="video-container">
        ''', unsafe_allow_html=True)
        st.video(p['video_url'])
        st.markdown('</div></div>', unsafe_allow_html=True)
        
        if st.button(f"🛒 COMPRAR YA: {p['nombre_producto']}", key=f"p_{p['id']}", use_container_width=True):
            ventana_pago(p, t['id'])
        st.markdown("<br>", unsafe_allow_html=True)

# --- VISTA: MALL ---
elif st.session_state.view == 'mall':
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg", use_container_width=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    for t in tiendas.data:
        if st.button(f"✨ ENTRAR A {t['nombre_comercio'].upper()}", key=t['id'], use_container_width=True):
            st.session_state.tienda_actual = t
            ir_a('tienda')

# --- VISTA: ADMIN (ACTUALIZADA) ---
elif st.session_state.view == 'admin':
    if st.button("⬅️ SALIR AL MALL"): ir_a('mall')
    st.title("🚀 PANEL DE PROPIETARIO")
    email_admin = st.text_input("Ingrese su Correo Registrado")
    
    if email_admin:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_admin).execute()
        if res.data:
            perf = res.data[0]
            tab1, tab2 = st.tabs(["📤 GESTIÓN DE PRODUCTOS", "📦 INVENTARIO EN VIVO"])
            
            with tab1:
                st.subheader("Configuración y Carga")
                with st.form("carga_full", clear_on_submit=True):
                    st.markdown("#### 1. Datos del Producto")
                    nom = st.text_input("Nombre del Artículo")
                    pre = st.number_input("Precio de Venta ($)", min_value=0.0)
                    vid = st.file_uploader("Video Vertical (MP4/MOV)", type=['mp4', 'mov'])
                    
                    st.divider()
                    st.markdown("#### 2. Datos de Pago (Se verán en el Carrito)")
                    # Los datos de pago se guardan aquí mismo
                    pago_actual = "" if perf.get('datos_pago') == "None" else perf.get('datos_pago', '')
                    pago_up = st.text_area("Cuentas Bancarias / Pago Móvil", value=pago_actual)
                    
                    if st.form_submit_button("🚀 GUARDAR Y PUBLICAR"):
                        # Primero actualizamos los datos de pago del perfil
                        supabase.table("perfiles_comercio").update({"datos_pago": pago_up}).eq("id", perf['id']).execute()
                        
                        # Luego cargamos el producto si hay video
                        if vid and nom:
                            path = f"videos/{perf['nombre_comercio']}/{random.randint(100,999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(path, vid.getvalue())
                            url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                            supabase.table("productos").insert({
                                "nombre_producto": nom, "precio": pre, 
                                "video_url": url_v, "comercio_relacionado": perf['nombre_comercio']
                            }).execute()
                            st.success("¡Datos de pago actualizados y Producto publicado!")
                            st.rerun()
                        else:
                            st.info("Datos de pago guardados. (No se subió producto porque faltaba nombre o video)")

            with tab2:
                st.subheader("Control de Stock")
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                if not items.data:
                    st.write("No tienes productos cargados.")
                else:
                    for i in items.data:
                        col_info, col_del = st.columns([4, 1])
                        col_info.write(f"**{i['nombre_producto']}** | `${i['precio']}`")
                        # Botón de borrar con clave única y rerun forzado
                        if col_del.button("🗑️", key=f"del_{i['id']}", use_container_width=True):
                            supabase.table("productos").delete().eq("id", i['id']).execute()
                            st.success(f"Eliminado: {i['nombre_producto']}")
                            st.rerun()
