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
# 2. CSS: ESTÉTICA NEÓN Y PREMIUM
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    
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
        color: #39FF14; /* Verde Neón */
        padding: 6px 20px;
        border-radius: 30px;
        font-weight: 900;
        font-size: 1.4rem;
        border: 2px solid #39FF14;
        box-shadow: 0 0 15px #39FF14, inset 0 0 5px #39FF14;
        z-index: 1000;
        text-shadow: 0 0 5px #39FF14;
    }

    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #8A6E2F 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        transition: 0.3s all !important;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VENTANA DE COMPRA CON CALCULADORA
# ==========================================
@st.dialog("💎 MI CARRITO PLATINUM")
def ventana_pago(producto, tienda_id):
    # Traer datos frescos de la tienda para asegurar los datos de pago
    res = supabase.table("perfiles_comercio").select("*").eq("id", tienda_id).single().execute()
    tienda = res.data
    
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    
    # CALCULADORA DE CANTIDAD
    col_cant, col_total = st.columns([1, 1])
    cantidad = col_cant.number_input("Cantidad", min_value=1, value=1, step=1)
    total_pagar = float(producto['precio']) * cantidad
    col_total.metric("TOTAL A PAGAR", f"${total_pagar:,.2f}")
    
    st.divider()
    
    # MOSTRAR DATOS DE PAGO (IMAGEN O TEXTO)
    st.markdown("#### 🏦 Datos de Pago del Comercio")
    info_pago = tienda.get('datos_pago')
    
    if info_pago:
        if "http" in info_pago:
            st.image(info_pago, caption="Transfiere a estos datos", use_container_width=True)
        else:
            st.info(info_pago)
    else:
        st.warning("El vendedor no ha cargado imagen de pago aún.")

    st.divider()
    ref = st.text_input("Ingresa Número de Referencia")
    
    if st.button("📲 FINALIZAR Y ENVIAR TICKET", use_container_width=True):
        if ref:
            # Ticket con Nombre del Comercio y Cantidad
            msj = (
                f"✨ *NUEVO PEDIDO PLATINUM*\n"
                f"🏪 *Comercio:* {tienda['nombre_comercio']}\n"
                f"--------------------------\n"
                f"📦 *Producto:* {producto['nombre_producto']}\n"
                f"🔢 *Cantidad:* {cantidad}\n"
                f"💰 *Total:* ${total_pagar:,.2f}\n"
                f"🎫 *Ref:* {ref}\n"
                f"--------------------------\n"
                f"✅ *Por favor confirme el pago.*"
            )
            url_wa = f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}"
            st.link_button("🚀 IR A WHATSAPP", url_wa)
        else:
            st.error("Por favor, ingresa la referencia del pago.")

# ==========================================
# 4. VISTAS
# ==========================================

with st.sidebar:
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg")
    st.button("🏠 MALL", on_click=ir_a, args=('mall',), use_container_width=True)
    st.button("⚙️ ADMIN", on_click=ir_a, args=('admin',), use_container_width=True)

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
        
        if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"btn_{p['id']}", use_container_width=True):
            ventana_pago(p, t['id'])

# --- MALL ---
elif st.session_state.view == 'mall':
    st.title("🏙️ PLATINUM MALL")
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    cols = st.columns(2)
    for idx, t in enumerate(tiendas.data):
        with cols[idx % 2]:
            if st.button(f"✨ {t['nombre_comercio'].upper()}", key=f"mall_{t['id']}", use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- ADMIN ---
elif st.session_state.view == 'admin':
    st.title("🚀 PANEL DE CONTROL")
    mail = st.text_input("Correo del Dueño")
    
    if mail:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
        if res.data:
            perf = res.data[0]
            t1, t2 = st.tabs(["📤 CARGA RÁPIDA", "📦 INVENTARIO"])
            
            with t1:
                st.write("📸 **Foto de Datos de Pago** (Solo si deseas cambiarla)")
                cam_pago = st.camera_input("Capturar", key="pago_cam")
                
                with st.form("quick_form", clear_on_submit=True):
                    st.write("### Datos del Nuevo Producto")
                    n = st.text_input("Nombre")
                    p = st.number_input("Precio ($)", min_value=0.0)
                    v = st.file_uploader("Video", type=['mp4', 'mov'])
                    
                    if st.form_submit_button("🚀 PUBLICAR PRODUCTO Y ACTUALIZAR PAGO"):
                        # Actualizar imagen de pago si se tomó una
                        if cam_pago:
                            p_path = f"pagos/{perf['id']}_pago.jpg"
                            supabase.storage.from_("fotos_productos").upload(p_path, cam_pago.getvalue(), {"upsert": "true"})
                            p_url = supabase.storage.from_("fotos_productos").get_public_url(p_path)
                            supabase.table("perfiles_comercio").update({"datos_pago": p_url}).eq("id", perf['id']).execute()

                        if n and v:
                            v_path = f"videos/{perf['id']}_{random.randint(100,999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(v_path, v.getvalue())
                            v_url = supabase.storage.from_("fotos_productos").get_public_url(v_path)
                            
                            supabase.table("productos").insert({
                                "nombre_producto": n, "precio": p, 
                                "video_url": v_url, "comercio_relacionado": perf['nombre_comercio']
                            }).execute()
                            st.success("¡Todo actualizado con éxito!")
                            st.rerun()

            with t2:
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    c1, c2 = st.columns([4,1])
                    c1.write(f"**{i['nombre_producto']}** | ${i['precio']}")
                    if c2.button("🗑️", key=f"del_{i['id']}"):
                        supabase.table("productos").delete().eq("id", i['id']).execute()
                        st.rerun()
