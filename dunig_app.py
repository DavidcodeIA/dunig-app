import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONEXIÓN Y CONFIGURACIÓN OFICIAL
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="expanded")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Lógica de Planes
def obtener_limite_plan(nombre_plan):
    planes = {"BRONCE": 5, "PLATINUM": 15, "DIAMANTE": 50}
    return planes.get(str(nombre_plan).upper(), 5)

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS: MARCA BLANCA Y SIDEBAR VISIBLE
# ==========================================
st.markdown("""
    <style>
    /* OCULTAR PUBLICIDAD DE STREAMLIT */
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ASEGURAR QUE EL BOTÓN DEL SIDEBAR SEA VISIBLE EN MÓVILES */
    .st-emotion-cache-zq5wmm {display: flex !important;} 
    
    /* ESTÉTICA LUXURY */
    .main { background-color: #000000; color: #ffffff; }
    
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 2px solid #D4AF37;
        visibility: visible !important;
    }
    
    /* Botones Dorados */
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #8A6E2F 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold;
        border: none;
    }
    
    /* Burbuja Neón */
    .price-bubble {
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(0, 0, 0, 0.8);
        color: #39FF14; 
        padding: 8px 20px;
        border-radius: 30px;
        font-weight: 900;
        font-size: 1.2rem;
        border: 2px solid #39FF14;
        z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. NAVEGACIÓN LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>D'UNIG</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; margin-top:-20px; color:gray;'>LUXURY EDITION</p>", unsafe_allow_html=True)
    st.divider()
    
    # Botones de navegación principal
    st.button("🏠 MALL PRINCIPAL", on_click=ir_a, args=('mall',), use_container_width=True)
    st.button("⚙️ PANEL DE CONTROL", on_click=ir_a, args=('admin',), use_container_width=True)
    
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2026 D'UNIG LUXURY")

# ==========================================
# 4. VENTANA DE COMPRA
# ==========================================
@st.dialog("💎 COMPRA LUXURY")
def ventana_pago(producto, tienda_id):
    res = supabase.table("perfiles_comercio").select("*").eq("id", tienda_id).single().execute()
    tienda = res.data
    st.markdown(f"### {producto['nombre_producto']}")
    cant = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cant
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.info(f"Pagar a: {tienda.get('datos_pago', 'Consultar')}")
    ref = st.text_input("Referencia de Pago")
    if st.button("📲 ENVIAR PEDIDO"):
        if ref:
            msj = f"💎 *PEDIDO LUXURY*\n📦 *Prod:* {producto['nombre_producto']}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            st.link_button("Ir a WhatsApp", f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}")
        else: st.error("Falta la referencia.")

# ==========================================
# 5. VISTAS PRINCIPALES
# ==========================================

# --- MALL ---
if st.session_state.view == 'mall':
    st.title("🏙️ LUXURY MALL")
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    cols = st.columns(2)
    for idx, t in enumerate(tiendas.data):
        with cols[idx % 2]:
            if st.button(f"✨ {t['nombre_comercio'].upper()}", key=f"mall_{t['id']}", use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.title(f"✨ {t['nombre_comercio']}")
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    for p in prods.data:
        st.markdown(f'<div style="position: relative;"><div class="price-bubble">${p["precio"]}</div></div>', unsafe_allow_html=True)
        st.video(p['video_url'])
        if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"p_{p['id']}", use_container_width=True):
            ventana_pago(p, t['id'])

# --- ADMIN ---
elif st.session_state.view == 'admin':
    st.title("🚀 PANEL ADMIN")
    mail = st.text_input("Email de acceso")
    if mail:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
        if res.data:
            perf = res.data[0]
            plan = perf.get('plan', 'BRONCE')
            limite = obtener_limite_plan(plan)
            
            # Info de Plan
            st.subheader(f"Plan: {plan}")
            res_c = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            actual = res_c.count if res_c.count else 0
            st.progress(min(actual/limite, 1.0))
            
            t_add, t_inv, t_set = st.tabs(["➕ SUBIR", "📦 INVENTARIO", "⚙️ PAGOS"])
            
            with t_set:
                pago_input = st.text_input("Datos de Pago", value=perf.get('datos_pago', ''))
                if st.button("GUARDAR DATOS"):
                    supabase.table("perfiles_comercio").update({"datos_pago": pago_input}).eq("id", perf['id']).execute()
                    st.success("Guardado")

            with t_add:
                if actual >= limite: st.error("Límite de plan lleno.")
                else:
                    with st.form("add"):
                        n = st.text_input("Nombre")
                        p = st.number_input("Precio")
                        v = st.file_uploader("Video")
                        if st.form_submit_button("PUBLICAR"):
                            path = f"videos/{random.randint(100,999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(path, v.getvalue())
                            url = supabase.storage.from_("fotos_productos").get_public_url(path)
                            supabase.table("productos").insert({"nombre_producto":n, "precio":p, "video_url":url, "comercio_relacionado":perf['nombre_comercio']}).execute()
                            st.rerun()

            with t_inv:
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    with st.expander(f"Editar {i['nombre_producto']}"):
                        if st.button("ELIMINAR", key=f"del_{i['id']}"):
                            supabase.table("productos").delete().eq("id", i['id']).execute()
                            st.rerun()
