import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN DE ALTO RENDIMIENTO
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

PLANES = {
    "BRONCE": 5,
    "PLATINUM": 15,
    "DIAMANTE": 50
}

# --- LÓGICA DE NAVEGACIÓN ---
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        animation: shimmer 5s infinite linear !important;
        color: #000 !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
    }

    .luxury-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    .price-bubble {
        position: absolute; top: 20px; right: 20px;
        background: rgba(0, 0, 0, 0.9); color: #39FF14; 
        padding: 8px 20px; border-radius: 50px;
        font-weight: 900; border: 2px solid #39FF14;
        z-index: 10;
    }

    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS Y FUNCIONES
# ==========================================
@st.dialog("💎 CARRITO D'UNIG LUXURY")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    col_cant, col_total = st.columns(2)
    cantidad = col_cant.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    col_total.metric("TOTAL", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **PAGO:** {tienda.get('datos_pago', 'Consultar')}")
    ref = st.text_input("Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Prod:* {producto['nombre_producto']}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            st.link_button("WHATSAPP", f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}")
        else: st.error("Falta referencia")

# ==========================================
# 4. CUERPO DE LA APP
# ==========================================

if not es_admin:
    # --- VISTA CLIENTE ---
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("🔍 Buscar tiendas...")
        res = supabase.table("perfiles_comercio").select("*").execute()
        tiendas = [t for t in res.data if busqueda.lower() in t['nombre_comercio'].lower()]
        
        cols = st.columns(2)
        for idx, t in enumerate(tiendas):
            with cols[idx % 2]:
                st.markdown(f"<div class='luxury-card'><h3 style='text-align:center;'>{t['nombre_comercio'].upper()}</h3>", unsafe_allow_html=True)
                if st.button("VISITAR", key=f"t_{t['id']}", use_container_width=True):
                    st.session_state.tienda_actual = t
                    ir_a('tienda')
                st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        st.button("⬅️ VOLVER", on_click=ir_a, args=('mall',))
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        for p in prods.data:
            st.markdown(f"<div style='position: relative;'><div class='price-bubble'>${p['precio']}</div></div>", unsafe_allow_html=True)
            st.video(p['video_url'])
            if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"p_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.divider()

else:
    # --- PANEL ADMIN ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ CONTROL LUXURY</h1>", unsafe_allow_html=True)
    mail = st.text_input("Email de Propietario")
    if mail:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
        if res.data:
            perf = res.data[0]
            plan = perf.get('plan', 'BRONCE').upper()
            limite = PLANES.get(plan, 5)
            res_c = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            total_p = res_c.count if res_c.count else 0
            
            st.markdown(f"<div class='luxury-card'><h3>Bienvenido, {perf['nombre_comercio']}</h3>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            col_a.metric("Plan", plan)
            col_b.metric("Cupos", f"{total_p}/{limite}")
            st.progress(min(total_p/limite, 1.0))
            st.markdown("</div>", unsafe_allow_html=True)

            t1, t2, t3, t4 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS", "💎 MI PLAN"])
            
            with t1:
                if total_p >= limite: st.error("Límite alcanzado. Sube de plan.")
                else:
                    with st.form("p", clear_on_submit=True):
                        n = st.text_input("Nombre")
                        pr = st.number_input("Precio", min_value=0.0)
                        v = st.file_uploader("Video", type=['mp4'])
                        if st.form_submit_button("PUBLICAR"):
                            if n and v:
                                path = f"v/{random.randint(1,9999)}.mp4"
                                supabase.storage.from_("fotos_productos").upload(path, v.getvalue())
                                url = supabase.storage.from_("fotos_productos").get_public_url(path)
                                supabase.table("productos").insert({"nombre_producto":n, "precio":pr, "video_url":url, "comercio_relacionado":perf['nombre_comercio']}).execute()
                                st.rerun()

            with t2:
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    with st.expander(f"{i['nombre_producto']}"):
                        if st.button("ELIMINAR", key=i['id']):
                            supabase.table("productos").delete().eq("id", i['id']).execute()
                            st.rerun()

            with t3:
                p_inf = st.text_area("Datos de cobro", value=str(perf.get('datos_pago', '')))
                if st.button("GUARDAR"):
                    supabase.table("perfiles_comercio").update({"datos_pago": p_inf}).eq("id", perf['id']).execute()
                    st.success("Guardado")

            with t4:
                st.markdown("### Membresía Luxury")
                c1, c2 = st.columns(2)
                c1.link_button("💎 PAGAR PLATINUM", "https://tu-link.com")
                c2.link_button("👑 PAGAR DIAMANTE", "https://tu-link.com")
                with st.expander("Reportar Pago"):
                    rf = st.text_input("Referencia")
                    if st.button("ENVIAR REPORT"):
                        st.link_button("Confirmar WA", f"https://wa.me/TU_NUMERO?text=Pago_{rf}")
        else: st.error("No registrado")
