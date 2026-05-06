import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONEXIÓN Y CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="expanded")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# DICCIONARIO DE PLANES DE SERVICIO
PLANES = {
    "BRONCE": 5,
    "PLATINUM": 15,
    "DIAMANTE": 50
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS: ESTÉTICA MEJORADA
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 2px solid #D4AF37;
    }
    
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

    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #8A6E2F 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. PANEL LATERAL
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>D'UNIG</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Luxury Edition</p>", unsafe_allow_html=True)
    st.divider()
    st.button("🏠 MALL PRINCIPAL", on_click=ir_a, args=('mall',), use_container_width=True)
    st.button("⚙️ PANEL DE CONTROL", on_click=ir_a, args=('admin',), use_container_width=True)

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================

# --- VISTA: MALL ---
if st.session_state.view == 'mall':
    st.title("🏙️ D'UNIG MALL")
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    cols = st.columns(2)
    for idx, t in enumerate(tiendas.data):
        with cols[idx % 2]:
            if st.button(f"✨ {t['nombre_comercio'].upper()}", key=f"ml_{t['id']}", use_container_width=True):
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
        st.markdown(f"**{p['nombre_producto']}**")
        st.divider()

# --- VISTA: ADMIN (CON PLANES DE SERVICIO) ---
elif st.session_state.view == 'admin':
    st.title("🚀 PANEL DE CONTROL")
    mail = st.text_input("Correo de propietario")
    
    if mail:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
        if res.data:
            perf = res.data[0]
            
            # Obtener plan del comercio (por defecto Bronce si no existe)
            plan_usuario = perf.get('plan', 'BRONCE').upper()
            limite_actual = PLANES.get(plan_usuario, 5)
            
            # Cabecera de suscripción
            c1, c2 = st.columns([2, 1])
            c1.metric("PLAN ACTUAL", plan_usuario)
            if c2.button("⚡ SUBIR NIVEL"):
                st.toast("Contacta a soporte para cambiar tu plan.")

            # Conteo de productos
            res_c = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            total_p = res_c.count if res_c.count else 0
            
            st.write(f"📊 **Uso de Inventario:** {total_p} de {limite_actual} productos")
            st.progress(min(total_p / limite_actual, 1.0))
            st.divider()

            t_add, t_inv = st.tabs(["➕ AGREGAR", "📦 GESTIONAR"])

            with t_add:
                if total_p >= limite_actual:
                    st.error(f"Has alcanzado el límite de tu plan {plan_usuario} ({limite_actual} productos).")
                    st.info("Borra productos antiguos o mejora tu plan para seguir publicando.")
                else:
                    with st.form("new_p", clear_on_submit=True):
                        n = st.text_input("Nombre del Producto")
                        p = st.number_input("Precio ($)", min_value=0.0)
                        v = st.file_uploader("Video publicitario", type=['mp4', 'mov'])
                        if st.form_submit_button("🚀 PUBLICAR"):
                            if n and v:
                                v_ext = v.name.split('.')[-1]
                                v_path = f"videos/{perf['id']}_{random.randint(1000,9999)}.{v_ext}"
                                supabase.storage.from_("fotos_productos").upload(v_path, v.getvalue())
                                v_url = supabase.storage.from_("fotos_productos").get_public_url(v_path)
                                supabase.table("productos").insert({
                                    "nombre_producto": n, "precio": p, "video_url": v_url, 
                                    "comercio_relacionado": perf['nombre_comercio']
                                }).execute()
                                st.rerun()

            with t_inv:
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    with st.expander(f"📝 {i['nombre_producto']}"):
                        if st.button("🗑️ ELIMINAR PRODUCTO", key=f"del_{i['id']}"):
                            supabase.table("productos").delete().eq("id", i['id']).execute()
                            st.rerun()
