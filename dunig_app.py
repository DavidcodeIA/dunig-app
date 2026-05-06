import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONEXIÓN Y CONFIGURACIÓN OFICIAL
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Lógica de Negocio: Capacidad por Plan
def obtener_limite_plan(nombre_plan):
    planes = {
        "BRONCE": 5,
        "PLATINUM": 15,
        "DIAMANTE": 50
    }
    return planes.get(str(nombre_plan).upper(), 5)

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS: MARCA BLANCA (LIMPIEZA TOTAL)
# ==========================================
st.markdown("""
    <style>
    /* OCULTAR ELEMENTOS DE STREAMLIT (PUBLICIDAD DE TERCEROS) */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stStatusWidget"] {display: none;}
    
    /* ESTÉTICA LUXURY: NEGRO Y DORADO */
    .main { background-color: #000000; color: #ffffff; }
    
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 2px solid #D4AF37;
    }
    
    /* Botones Premium */
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #8A6E2F 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: bold;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
    }

    /* Burbuja de Precio Neón */
    .price-bubble {
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(0, 0, 0, 0.85);
        color: #39FF14; 
        padding: 8px 22px;
        border-radius: 30px;
        font-weight: 900;
        font-size: 1.3rem;
        border: 2px solid #39FF14;
        box-shadow: 0 0 12px #39FF14;
        z-index: 100;
    }

    .block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. COMPONENTES DE INTERFAZ (DIÁLOGOS)
# ==========================================
@st.dialog("💎 CARRITO D'UNIG LUXURY")
def ventana_pago(producto, tienda_id):
    res = supabase.table("perfiles_comercio").select("*").eq("id", tienda_id).single().execute()
    tienda = res.data
    
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    col_cant, col_total = st.columns(2)
    cantidad = col_cant.number_input("Cant.", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    col_total.metric("TOTAL", f"${total:,.2f}")
    
    st.divider()
    st.markdown("#### 💳 MÉTODO DE PAGO")
    datos_pago = tienda.get('datos_pago', 'No configurado')
    st.info(f"Instrucciones:\n\n**{datos_pago}**")

    ref = st.text_input("Nro. de Referencia")
    if st.button("📲 CONFIRMAR POR WHATSAPP", use_container_width=True):
        if ref:
            msj = (
                f"💎 *NUEVA COMPRA LUXURY*\n"
                f"🏪 *Tienda:* {tienda['nombre_comercio']}\n"
                f"📦 *Producto:* {producto['nombre_producto']}\n"
                f"🔢 *Cant:* {cantidad} | *Total:* ${total:,.2f}\n"
                f"🎫 *Ref:* {ref}\n"
                f"--------------------------"
            )
            url_wa = f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}"
            st.link_button("🚀 ABRIR CHAT", url_wa)
        else:
            st.error("La referencia es obligatoria.")

# ==========================================
# 4. NAVEGACIÓN Y VISTAS
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>D'UNIG</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; margin-top:-20px;'>LUXURY EDITION</p>", unsafe_allow_html=True)
    st.divider()
    st.button("🏠 MALL PRINCIPAL", on_click=ir_a, args=('mall',), use_container_width=True)
    st.button("⚙️ PANEL CONTROL", on_click=ir_a, args=('admin',), use_container_width=True)

# --- VISTA: MALL ---
if st.session_state.view == 'mall':
    st.title("🏙️ LUXURY MALL")
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    cols = st.columns(2)
    for idx, t in enumerate(tiendas.data):
        with cols[idx % 2]:
            if st.button(f"✨ {t['nombre_comercio'].upper()}", key=f"m_{t['id']}", use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA: TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    
    for p in prods.data:
        st.markdown(f'<div style="position: relative;"><div class="price-bubble">${p["precio"]}</div></div>', unsafe_allow_html=True)
        st.video(p['video_url'])
        if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"btn_{p['id']}", use_container_width=True):
            ventana_pago(p, t['id'])
        st.markdown("<br>", unsafe_allow_html=True)

# --- VISTA: ADMIN ---
elif st.session_state.view == 'admin':
    st.title("🚀 PANEL DE CONTROL")
    mail = st.text_input("Email del Propietario")
    
    if mail:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
        if res.data:
            perf = res.data[0]
            # Gestión de Plan
            plan = perf.get('plan', 'BRONCE').upper()
            limite = obtener_limite_plan(plan)
            
            # Encabezado de Plan
            c1, c2 = st.columns([2,1])
            c1.subheader(f"Nivel: {plan}")
            if c2.button("⚡ MEJORAR"):
                st.info("Contacta a D'UNIG para subir a DIAMANTE.")
            
            # Barra de Inventario
            res_c = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            actual = res_c.count if res_c.count else 0
            st.progress(min(actual/limite, 1.0))
            st.write(f"Inventario: {actual} de {limite} permitidos.")

            t_add, t_inv, t_set = st.tabs(["➕ SUBIR", "📦 PRODUCTOS", "⚙️ AJUSTES"])

            with t_set:
                st.write("### Datos de Cobro")
                np = st.text_input("Datos de Pago (Texto/Números)", value=str(perf.get('datos_pago', '')))
                if st.button("💾 GUARDAR CAMBIOS"):
                    supabase.table("perfiles_comercio").update({"datos_pago": np}).eq("id", perf['id']).execute()
                    st.success("Ajustes actualizados.")

            with t_add:
                if actual >= limite:
                    st.error("Límite excedido. Borra productos o mejora tu plan.")
                else:
                    with st.form("new_p", clear_on_submit=True):
                        n = st.text_input("Nombre")
                        p = st.number_input("Precio ($)", min_value=0.0)
                        v = st.file_uploader("Video", type=['mp4', 'mov'])
                        if st.form_submit_button("🚀 PUBLICAR"):
                            if n and v:
                                path = f"videos/{perf['id']}_{random.randint(100,999)}.mp4"
                                supabase.storage.from_("fotos_productos").upload(path, v.getvalue())
                                url = supabase.storage.from_("fotos_productos").get_public_url(path)
                                supabase.table("productos").insert({
                                    "nombre_producto": n, "precio": p, "video_url": url, 
                                    "comercio_relacionado": perf['nombre_comercio']
                                }).execute()
                                st.rerun()

            with t_inv:
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    with st.expander(f"📦 {i['nombre_producto']}"):
                        if st.button("🗑️ ELIMINAR", key=f"d_{i['id']}"):
                            supabase.table("productos").delete().eq("id", i['id']).execute()
                            st.rerun()
