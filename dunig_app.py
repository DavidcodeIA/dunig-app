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
# 2. CSS: ESTÉTICA DORADO & NEÓN
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    
    /* Sidebar Dorado */
    [data-testid="stSidebar"] {
        background-color: #1a1a1a !important;
        border-right: 2px solid #D4AF37;
    }
    
    [data-testid="stSidebar"] .stButton>button {
        background: #D4AF37 !important;
        color: #000 !important;
        font-weight: bold;
    }

    /* Contenedor de Video */
    .video-container {
        width: 100%;
        border-radius: 25px;
        border: 2px solid #D4AF37;
        overflow: hidden;
        margin-bottom: 15px;
        position: relative;
    }

    /* Burbuja Precio Neón */
    .price-bubble {
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(0, 0, 0, 0.8);
        color: #39FF14; 
        padding: 6px 20px;
        border-radius: 30px;
        font-weight: 900;
        font-size: 1.3rem;
        border: 2px solid #39FF14;
        box-shadow: 0 0 10px #39FF14;
        z-index: 100;
    }

    /* Botones Dorados */
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #8A6E2F 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VENTANA DE COMPRA (CARRITO)
# ==========================================
@st.dialog("💎 MI CARRITO PLATINUM")
def ventana_pago(producto, tienda_id):
    # Obtener datos frescos del comercio (especialmente los datos de pago)
    res = supabase.table("perfiles_comercio").select("*").eq("id", tienda_id).single().execute()
    tienda = res.data
    
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    
    col_cant, col_total = st.columns([1, 1])
    cantidad = col_cant.number_input("Cantidad", min_value=1, value=1, step=1)
    total_pagar = float(producto['precio']) * cantidad
    col_total.metric("TOTAL A PAGAR", f"${total_pagar:,.2f}")
    
    st.divider()
    
    # MOSTRAR DATOS MIXTOS (NÚMEROS Y TEXTO)
    st.markdown("#### 💳 DATOS DE PAGO")
    datos_pago = tienda.get('datos_pago')
    
    if datos_pago:
        st.info(f"Realiza tu transferencia o pago móvil a:\n\n**{datos_pago}**")
    else:
        st.warning("El comercio aún no ha configurado sus datos de pago.")

    st.divider()
    ref = st.text_input("Ingresa el Número de Referencia")
    
    if st.button("📲 FINALIZAR Y ENVIAR WHATSAPP", use_container_width=True):
        if ref:
            msj = (
                f"✨ *NUEVO PEDIDO PLATINUM*\n"
                f"🏪 *Comercio:* {tienda['nombre_comercio']}\n"
                f"--------------------------\n"
                f"📦 *Producto:* {producto['nombre_producto']}\n"
                f"🔢 *Cantidad:* {cantidad}\n"
                f"💰 *Total:* ${total_pagar:,.2f}\n"
                f"🎫 *Ref:* {ref}\n"
                f"💳 *Pago a:* {datos_pago}\n"
                f"--------------------------\n"
                f"✅ *Confirmación pendiente.*"
            )
            url_wa = f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}"
            st.link_button("🚀 IR AL CHAT DEL VENDEDOR", url_wa)
        else:
            st.error("Es obligatorio ingresar la referencia de pago.")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================

with st.sidebar:
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>D'UNIG</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:0.8rem;'>PLATINUM EDITION</p>", unsafe_allow_html=True)
    st.divider()
    st.button("🏠 MALL PRINCIPAL", on_click=ir_a, args=('mall',), use_container_width=True)
    st.button("⚙️ PANEL DE CONTROL", on_click=ir_a, args=('admin',), use_container_width=True)

# --- VISTA: TIENDA ---
if st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    
    for p in prods.data:
        # Contenedor relativo para que la burbuja flote sobre el video
        st.markdown(f'''
            <div style="position: relative;">
                <div class="price-bubble">${p['precio']}</div>
            </div>
        ''', unsafe_allow_html=True)
        st.video(p['video_url'])
        
        if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"shop_{p['id']}", use_container_width=True):
            ventana_pago(p, t['id'])
        st.markdown("<br>", unsafe_allow_html=True)

# --- VISTA: ADMIN (GESTIÓN TOTAL) ---
elif st.session_state.view == 'admin':
    st.title("🚀 PANEL DE ADMINISTRACIÓN")
    mail = st.text_input("Correo del Propietario")
    
    if mail:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
        if res.data:
            perf = res.data[0]
            
            # SECCIÓN DE DATOS DE PAGO (TEXTO Y NÚMEROS)
            st.write("### 💳 Configuración de Cobro")
            # Usamos text_input para que pueda poner Banco, Cédula, Teléfono, etc.
            nuevo_pago = st.text_input("Datos de Pago Móvil / Transferencia", 
                                        value=str(perf.get('datos_pago', '')),
                                        help="Ej: Banesco, 0414-1234567, V-12345678")
            
            if st.button("💾 Guardar Datos de Pago"):
                supabase.table("perfiles_comercio").update({"datos_pago": nuevo_pago}).eq("id", perf['id']).execute()
                st.success("Datos de pago actualizados.")

            st.divider()

            # PESTAÑAS
            t_nuevo, t_inventario = st.tabs(["➕ AGREGAR", "📦 INVENTARIO"])

            with t_nuevo:
                with st.form("form_new", clear_on_submit=True):
                    st.write("### Nuevo Producto")
                    n = st.text_input("Nombre")
                    p = st.number_input("Precio ($)", min_value=0.0)
                    v = st.file_uploader("Video", type=['mp4', 'mov'])
                    
                    if st.form_submit_button("🚀 PUBLICAR"):
                        if n and v:
                            v_path = f"videos/{perf['id']}_{random.randint(100,999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(v_path, v.getvalue())
                            v_url = supabase.storage.from_("fotos_productos").get_public_url(v_path)
                            
                            supabase.table("productos").insert({
                                "nombre_producto": n, "precio": p, 
                                "video_url": v_url, "comercio_relacionado": perf['nombre_comercio']
                            }).execute()
                            st.success("¡Producto en línea!")
                            st.rerun()

            with t_inventario:
                st.write("### Mis Productos")
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                
                for i in items.data:
                    with st.expander(f"📦 {i['nombre_producto']} - ${i['precio']}"):
                        # EDITAR
                        nuevo_n = st.text_input("Editar Nombre", value=i['nombre_producto'], key=f"n_{i['id']}")
                        nuevo_p = st.number_input("Editar Precio", value=float(i['precio']), key=f"p_{i['id']}")
                        
                        c1, c2 = st.columns(2)
                        if c1.button("💾 GUARDAR", key=f"sv_{i['id']}", use_container_width=True):
                            supabase.table("productos").update({
                                "nombre_producto": nuevo_n,
                                "precio": nuevo_p
                            }).eq("id", i['id']).execute()
                            st.rerun()
                        
                        if c2.button("🗑️ BORRAR", key=f"dl_{i['id']}", use_container_width=True):
                            supabase.table("productos").delete().eq("id", i['id']).execute()
                            st.rerun()

# --- VISTA: MALL ---
elif st.session_state.view == 'mall':
    st.title("🏙️ PLATINUM MALL")
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    cols = st.columns(2)
    for idx, t in enumerate(tiendas.data):
        with cols[idx % 2]:
            if st.button(f"✨ {t['nombre_comercio'].upper()}", key=f"m_{t['id']}", use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')
