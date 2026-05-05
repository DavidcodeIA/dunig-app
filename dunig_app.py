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
# 2. CSS: BURBUJA FLOTANTE Y DISEÑO 3D
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; }
    
    .fixed-back {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 2000;
    }

    .product-card {
        position: relative;
        width: 100%;
        margin-bottom: 20px;
    }

    .video-container {
        width: 100%;
        border-radius: 30px;
        border: 3px solid #D4AF37;
        overflow: hidden;
        box-shadow: 0 20px 50px rgba(0,0,0,0.9);
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
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VENTANA DE PAGO (CORRECCIÓN TOTAL)
# ==========================================
@st.dialog("💎 PROCESAR PEDIDO")
def ventana_pago(producto, comercio_id):
    # CONSULTA EN VIVO: Traemos los datos directo de la DB al abrir la ventana
    res = supabase.table("perfiles_comercio").select("*").eq("id", comercio_id).single().execute()
    tienda = res.data
    
    st.markdown(f"### 🛍️ {producto['nombre_producto']}")
    st.markdown(f"**Monto:** `${producto['precio']}`")
    st.divider()
    
    st.markdown("### 🏦 Datos de Pago")
    pago_info = tienda.get('datos_pago')
    
    if not pago_info or pago_info == "None":
        st.error("⚠️ El vendedor aún no ha configurado sus datos de pago.")
    else:
        st.success("Cuentas autorizadas:")
        st.info(pago_info)
    
    ref = st.text_input("Número de Referencia")
    
    if st.button("📲 CONFIRMAR Y ENVIAR TICKET"):
        if ref:
            mensaje = (
                f"✨ *PEDIDO PLATINUM*\n\n"
                f"📦 *Producto:* {producto['nombre_producto']}\n"
                f"💰 *Precio:* ${producto['precio']}\n"
                f"🔢 *Ref:* {ref}\n"
                f"🏪 *Tienda:* {tienda['nombre_comercio']}"
            )
            url_wa = f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(mensaje)}"
            st.link_button("🚀 IR A WHATSAPP", url_wa)
        else:
            st.warning("Por favor, ingresa la referencia.")

# ==========================================
# 4. NAVEGACIÓN Y VISTAS
# ==========================================

with st.sidebar:
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg")
    if st.button("🏠 MALL", use_container_width=True): ir_a('mall')
    if st.button("⚙️ PANEL CONTROL", use_container_width=True): ir_a('admin')

# --- TIENDA ---
if st.session_state.view == 'tienda':
    st.markdown('<div class="fixed-back">', unsafe_allow_html=True)
    if st.button("⬅️"): ir_a('mall')
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
        
        if st.button(f"🛒 COMPRAR YA: {p['nombre_producto']}", key=f"btn_{p['id']}", use_container_width=True):
            ventana_pago(p, t['id'])
        st.markdown("<br>", unsafe_allow_html=True)

# --- MALL ---
elif st.session_state.view == 'mall':
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg", use_container_width=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    for t in tiendas.data:
        if st.button(f"✨ ENTRAR A {t['nombre_comercio'].upper()}", key=t['id'], use_container_width=True):
            st.session_state.tienda_actual = t
            ir_a('tienda')

# --- ADMIN (CON STOCK Y CARGA ACTIVADOS) ---
elif st.session_state.view == 'admin':
    if st.button("⬅️ VOLVER"): ir_a('mall')
    st.title("🚀 PANEL DE CONTROL")
    correo = st.text_input("Email del Propietario")
    
    if correo:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", correo).execute()
        if res.data:
            perf = res.data[0]
            tab1, tab2, tab3 = st.tabs(["📤 CARGAR PRODUCTO", "📦 STOCK / INVENTARIO", "💰 DATOS PAGO"])
            
            with tab1:
                st.subheader("Subir Nueva Mercancía")
                with st.form("form_carga", clear_on_submit=True):
                    nom_p = st.text_input("Nombre del Producto")
                    pre_p = st.number_input("Precio ($)", min_value=0.0)
                    vid_p = st.file_uploader("Video del Producto", type=['mp4', 'mov'])
                    if st.form_submit_button("🚀 PUBLICAR EN VITRINA"):
                        if vid_p and nom_p:
                            path = f"videos/{perf['nombre_comercio']}/{random.randint(100,999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(path, vid_p.getvalue())
                            url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                            supabase.table("productos").insert({
                                "nombre_producto": nom_p, 
                                "precio": pre_p, 
                                "video_url": url_v, 
                                "comercio_relacionado": perf['nombre_comercio']
                            }).execute()
                            st.success("¡Producto cargado con éxito!")

            with tab2:
                st.subheader("Tu Inventario Actual")
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**{i['nombre_producto']}** - ${i['precio']}")
                    if c2.button("🗑️ ELIMINAR", key=f"del_{i['id']}"):
                        supabase.table("productos").delete().eq("id", i['id']).execute()
                        st.rerun()

            with tab3:
                st.subheader("Configuración de Cobro")
                actual_pago = perf.get('datos_pago', '')
                nuevo_pago = st.text_area("Cuentas Bancarias / Pago Móvil", value="" if actual_pago == "None" else actual_pago, height=150)
                if st.button("💾 ACTUALIZAR MIS DATOS DE PAGO"):
                    supabase.table("perfiles_comercio").update({"datos_pago": nuevo_pago}).eq("id", perf['id']).execute()
                    st.success("¡Datos guardados! Ahora tus clientes podrán verlos.")
