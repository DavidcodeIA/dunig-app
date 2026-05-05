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
# 2. CSS: DORADO PREMIUM Y NEÓN
# ==========================================
st.markdown("""
    <style>
    /* Fondo y Texto General */
    .main { background-color: #000000; color: #ffffff; }
    
    /* Sidebar Dorado Invertido */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
        border-right: 2px solid #D4AF37;
    }
    
    /* Botones del Sidebar en Dorado */
    [data-testid="stSidebar"] .stButton>button {
        background: #D4AF37 !important;
        color: #000 !important;
        border: 1px solid #ffffff !important;
    }

    .fixed-back { position: fixed; top: 15px; left: 15px; z-index: 3000; }

    .video-container {
        width: 100%;
        border-radius: 25px;
        border: 2px solid #D4AF37;
        overflow: hidden;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
        margin-bottom: 15px;
        background-color: #000;
    }

    /* BURBUJA DE PRECIO COLOR NEÓN */
    .price-bubble {
        position: absolute;
        top: 15px;
        right: 15px;
        background: #000000;
        color: #39FF14; 
        padding: 6px 20px;
        border-radius: 30px;
        font-weight: 900;
        font-size: 1.4rem;
        border: 2px solid #39FF14;
        box-shadow: 0 0 15px #39FF14, inset 0 0 5px #39FF14;
        z-index: 1000;
        text-shadow: 0 0 5px #39FF14;
    }

    /* Botones de Compra Dorados */
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #8A6E2F 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VENTANA DE COMPRA (CORREGIDA)
# ==========================================
@st.dialog("💎 MI CARRITO PLATINUM")
def ventana_pago(producto, tienda_id):
    # BUSQUEDA CRÍTICA: Obtener datos de pago actualizados
    res = supabase.table("perfiles_comercio").select("*").eq("id", tienda_id).single().execute()
    tienda = res.data
    
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    
    col_cant, col_total = st.columns([1, 1])
    cantidad = col_cant.number_input("Cantidad", min_value=1, value=1, step=1)
    total_pagar = float(producto['precio']) * cantidad
    col_total.metric("TOTAL A PAGAR", f"${total_pagar:,.2f}")
    
    st.divider()
    
    # SECCIÓN DE DATOS DE PAGO
    st.markdown("#### 🏦 MÉTODO DE PAGO")
    info_pago = tienda.get('datos_pago')
    
    if info_pago:
        # Si es una URL de imagen de Supabase
        if "http" in info_pago:
            st.image(info_pago, caption="Escanea o usa estos datos para transferir", use_container_width=True)
        else:
            st.info(f"📝 **Instrucciones:**\n\n{info_pago}")
    else:
        st.error("⚠️ El vendedor no ha configurado sus datos de pago.")

    st.divider()
    ref = st.text_input("Ingresa el Número de Referencia de tu pago")
    
    if st.button("📲 CONFIRMAR PAGO Y ENVIAR", use_container_width=True):
        if ref:
            msj = (
                f"✨ *NUEVO PEDIDO PLATINUM*\n"
                f"🏪 *Comercio:* {tienda['nombre_comercio']}\n"
                f"--------------------------\n"
                f"📦 *Producto:* {producto['nombre_producto']}\n"
                f"🔢 *Cantidad:* {cantidad}\n"
                f"💰 *Total:* ${total_pagar:,.2f}\n"
                f"🎫 *Ref:* {ref}\n"
                f"--------------------------\n"
                f"✅ *Espero su confirmación.*"
            )
            url_wa = f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}"
            st.link_button("🚀 ENVIAR COMPROBANTE POR WHATSAPP", url_wa)
        else:
            st.error("Es obligatorio ingresar la referencia.")

# ==========================================
# 4. VISTAS
# ==========================================

with st.sidebar:
    # ELIMINADA LA FOTO ANTERIOR - SOLO BOTONES DORADOS
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>PLATINUM</h2>", unsafe_allow_html=True)
    st.divider()
    st.button("🏠 IR AL MALL", on_click=ir_a, args=('mall',), use_container_width=True)
    st.button("⚙️ PANEL SOCIO", on_click=ir_a, args=('admin',), use_container_width=True)

# --- VISTA TIENDA ---
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
        
        if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"btn_{p['id']}", use_container_width=True):
            ventana_pago(p, t['id'])

# --- VISTA MALL ---
elif st.session_state.view == 'mall':
    st.title("🏙️ PLATINUM MALL")
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    cols = st.columns(2)
    for idx, t in enumerate(tiendas.data):
        with cols[idx % 2]:
            if st.button(f"✨ {t['nombre_comercio'].upper()}", key=f"mall_{t['id']}", use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA ADMIN (MEJORADA) ---
elif st.session_state.view == 'admin':
    st.title("🚀 CONFIGURACIÓN DE SOCIO")
    mail = st.text_input("Ingresa tu correo de socio")
    
    if mail:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
        if res.data:
            perf = res.data[0]
            st.success(f"Bienvenido, {perf['nombre_comercio']}")
            
            t1, t2 = st.tabs(["⚡ GESTIÓN RÁPIDA", "📦 MIS PRODUCTOS"])
            
            with t1:
                st.info("💡 Captura tu QR o datos de pago aquí abajo.")
                cam_pago = st.camera_input("Capturar Datos de Pago")
                
                with st.form("admin_form"):
                    st.write("---")
                    st.write("### Subir Nuevo Producto")
                    n = st.text_input("Nombre del Producto")
                    p = st.number_input("Precio", min_value=0.0)
                    v = st.file_uploader("Video del Producto", type=['mp4', 'mov'])
                    
                    submit = st.form_submit_button("🌟 GUARDAR CAMBIOS")
                    
                    if submit:
                        # 1. Actualizar imagen de pago si se capturó una
                        if cam_pago:
                            p_path = f"pagos/{perf['id']}_pago.jpg"
                            supabase.storage.from_("fotos_productos").upload(p_path, cam_pago.getvalue(), {"upsert": "true"})
                            p_url = supabase.storage.from_("fotos_productos").get_public_url(p_path)
                            supabase.table("perfiles_comercio").update({"datos_pago": p_url}).eq("id", perf['id']).execute()
                            st.toast("Imagen de pago actualizada")

                        # 2. Subir producto si hay datos
                        if n and v:
                            v_path = f"videos/{perf['id']}_{random.randint(100,999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(v_path, v.getvalue())
                            v_url = supabase.storage.from_("fotos_productos").get_public_url(v_path)
                            supabase.table("productos").insert({
                                "nombre_producto": n, "precio": p, 
                                "video_url": v_url, "comercio_relacionado": perf['nombre_comercio']
                            }).execute()
                            st.success("Producto publicado con éxito")
                        
                        st.rerun()

            with t2:
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    c1, c2 = st.columns([4,1])
                    c1.write(f"**{i['nombre_producto']}** | ${i['precio']}")
                    if c2.button("🗑️", key=f"del_{i['id']}"):
                        supabase.table("productos").delete().eq("id", i['id']).execute()
                        st.rerun()
