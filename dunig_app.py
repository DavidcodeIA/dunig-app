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
# 2. CSS: DORADO PREMIUM Y DISEÑO
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
        border-right: 2px solid #D4AF37;
    }
    
    [data-testid="stSidebar"] .stButton>button {
        background: #D4AF37 !important;
        color: #000 !important;
        border: 1px solid #ffffff !important;
    }

    .video-container {
        width: 100%;
        border-radius: 25px;
        border: 2px solid #D4AF37;
        overflow: hidden;
        margin-bottom: 15px;
    }

    .price-bubble {
        position: absolute;
        top: 15px;
        right: 15px;
        background: #000000;
        color: #39FF14; 
        padding: 6px 20px;
        border-radius: 30px;
        font-weight: 900;
        border: 2px solid #39FF14;
        z-index: 1000;
    }

    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #8A6E2F 100%) !important;
        color: white !important;
        border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VENTANA DE COMPRA (CARRITO)
# ==========================================
@st.dialog("💎 MI CARRITO PLATINUM")
def ventana_pago(producto, tienda_id):
    res = supabase.table("perfiles_comercio").select("*").eq("id", tienda_id).single().execute()
    tienda = res.data
    
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    
    col_cant, col_total = st.columns([1, 1])
    cantidad = col_cant.number_input("Cantidad", min_value=1, value=1, step=1)
    total_pagar = float(producto['precio']) * cantidad
    col_total.metric("TOTAL A PAGAR", f"${total_pagar:,.2f}")
    
    st.divider()
    
    st.markdown("#### 📱 PAGO MÓVIL")
    pago_movil = tienda.get('datos_pago')
    
    if pago_movil:
        st.info(f"Realiza tu pago al número:\n\n**{pago_movil}**")
    else:
        st.warning("El comercio no tiene Pago Móvil configurado.")

    st.divider()
    ref = st.text_input("Referencia de Pago")
    
    if st.button("📲 FINALIZAR PEDIDO", use_container_width=True):
        if ref:
            msj = (
                f"✨ *NUEVO PEDIDO PLATINUM*\n"
                f"🏪 *Comercio:* {tienda['nombre_comercio']}\n"
                f"--------------------------\n"
                f"📦 *Producto:* {producto['nombre_producto']}\n"
                f"🔢 *Cantidad:* {cantidad}\n"
                f"💰 *Total:* ${total_pagar:,.2f}\n"
                f"🎫 *Ref:* {ref}\n"
                f"📱 *Pago Móvil:* {pago_movil}\n"
                f"--------------------------\n"
                f"✅ *Confirmación pendiente.*"
            )
            url_wa = f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}"
            st.link_button("🚀 ENVIAR A WHATSAPP", url_wa)
        else:
            st.error("Ingresa la referencia.")

# ==========================================
# 4. VISTAS PRINCIPALES
# ==========================================

with st.sidebar:
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>PLATINUM</h2>", unsafe_allow_html=True)
    st.divider()
    st.button("🏠 MALL", on_click=ir_a, args=('mall',), use_container_width=True)
    st.button("⚙️ ADMIN", on_click=ir_a, args=('admin',), use_container_width=True)

# --- TIENDA ---
if st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    for p in prods.data:
        st.markdown(f'<div style="position: relative;">', unsafe_allow_html=True)
        st.markdown(f'<div class="price-bubble">${p["precio"]}</div>', unsafe_allow_html=True)
        st.video(p['video_url'])
        if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"btn_{p['id']}", use_container_width=True):
            ventana_pago(p, t['id'])
        st.markdown(f'</div><br>', unsafe_allow_html=True)

# --- ADMIN (GESTIÓN COMPLETA) ---
elif st.session_state.view == 'admin':
    st.title("🚀 PANEL DE SOCIO")
    mail = st.text_input("Ingresa tu correo registrado")
    
    if mail:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
        if res.data:
            perf = res.data[0]
            
            # PAGO MÓVIL (FUERA DEL FORMULARIO PARA GUARDADO INDEPENDIENTE)
            st.write("### 💳 Configuración de Cobro")
            nuevo_pago_movil = st.text_input("Número de Pago Móvil", value=str(perf.get('datos_pago', '')))
            if st.button("💾 Actualizar Pago Móvil"):
                supabase.table("perfiles_comercio").update({"datos_pago": nuevo_pago_movil}).eq("id", perf['id']).execute()
                st.success("Pago Móvil actualizado.")

            st.divider()

            # PESTAÑAS DE GESTIÓN
            tab_nuevo, tab_inventario = st.tabs(["➕ NUEVO PRODUCTO", "📦 MIS PRODUCTOS"])

            with tab_nuevo:
                with st.form("nuevo_producto_form", clear_on_submit=True):
                    st.write("### Publicar Nuevo Item")
                    n = st.text_input("Nombre del Producto")
                    p = st.number_input("Precio ($)", min_value=0.0)
                    v = st.file_uploader("Subir Video (MP4/MOV)", type=['mp4', 'mov'])
                    
                    if st.form_submit_button("🌟 GUARDAR PRODUCTO"):
                        if n and v:
                            v_path = f"videos/{perf['id']}_{random.randint(1000,9999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(v_path, v.getvalue())
                            v_url = supabase.storage.from_("fotos_productos").get_public_url(v_path)
                            supabase.table("productos").insert({
                                "nombre_producto": n, "precio": p, 
                                "video_url": v_url, "comercio_relacionado": perf['nombre_comercio']
                            }).execute()
                            st.success("¡Producto publicado!")
                            st.rerun()
                        else:
                            st.error("Nombre y video son obligatorios.")

            with tab_inventario:
                st.write("### Gestionar Existencias")
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                
                if not items.data:
                    st.info("No tienes productos aún.")
                
                for i in items.data:
                    with st.expander(f"📦 {i['nombre_producto']} - ${i['precio']}"):
                        enombre = st.text_input("Nombre", value=i['nombre_producto'], key=f"e_n_{i['id']}")
                        eprecio = st.number_input("Precio", value=float(i['precio']), key=f"e_p_{i['id']}")
                        
                        col1, col2 = st.columns(2)
                        if col1.button("✅ GUARDAR", key=f"save_{i['id']}", use_container_width=True):
                            supabase.table("productos").update({
                                "nombre_producto": enombre,
                                "precio": eprecio
                            }).eq("id", i['id']).execute()
                            st.success("Editado")
                            st.rerun()
                            
                        if col2.button("🗑️ BORRAR", key=f"del_{i['id']}", use_container_width=True):
                            supabase.table("productos").delete().eq("id", i['id']).execute()
                            st.warning("Eliminado")
                            st.rerun()

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
