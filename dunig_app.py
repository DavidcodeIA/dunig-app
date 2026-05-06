import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONEXIÓN Y CONFIGURACIÓN OFICIAL
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="centered", 
    initial_sidebar_state="expanded"
)

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Lógica de Negocio: Planes de Servicios
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
# 2. CSS: MARCA BLANCA (OCULTAR TODO)
# ==========================================
st.markdown("""
    <style>
    /* 1. OCULTAR PUBLICIDAD INFERIOR DERECHA Y FOOTER */
    footer {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    header {visibility: hidden !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden !important;}
    
    /* 2. ESTÉTICA D'UNIG LUXURY */
    .main { background-color: #000000; color: #ffffff; }
    
    [data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 2px solid #D4AF37;
    }

    /* Botones Dorados Luxury */
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #8A6E2F 100%) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold;
        border: none !important;
        transition: 0.3s ease-in-out;
    }
    
    .stButton>button:hover {
        transform: scale(1.03);
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.4);
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
        font-size: 1.2rem;
        border: 2px solid #39FF14;
        box-shadow: 0 0 10px #39FF14;
        z-index: 100;
    }

    /* Burbuja de Upgrade para Planes */
    .upgrade-badge {
        background: #D4AF37;
        color: black;
        padding: 5px 15px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.8rem;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. PANEL LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='color:#D4AF37; text-align:center;'>D'UNIG</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; margin-top:-20px; color:gray;'>LUXURY EDITION</p>", unsafe_allow_html=True)
    st.divider()
    
    st.button("🏠 MALL PRINCIPAL", on_click=ir_a, args=('mall',), use_container_width=True)
    st.button("⚙️ PANEL DE CONTROL", on_click=ir_a, args=('admin',), use_container_width=True)
    
    st.markdown("<br><br>"*10, unsafe_allow_html=True)
    st.caption("D'UNIG LUXURY © 2026")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================

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
        st.markdown(f"**{p['nombre_producto']}**")
        st.divider()

# --- VISTA: ADMIN (GESTIÓN Y PLANES) ---
elif st.session_state.view == 'admin':
    st.title("🚀 PANEL DE CONTROL")
    mail = st.text_input("Ingresa tu correo de propietario")
    
    if mail:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
        if res.data:
            perf = res.data[0]
            
            # --- SECCIÓN DE PLANES ---
            plan_actual = perf.get('plan', 'BRONCE').upper()
            limite = obtener_limite_plan(plan_actual)
            
            c1, c2 = st.columns([2, 1])
            c1.info(f"💎 **Plan Actual:** {plan_actual}")
            with c2:
                if st.button("⚡ MEJORAR PLAN"):
                    st.toast("Redirigiendo a soporte para upgrade...")
                    # Aquí puedes poner un link de pago o contacto
            
            res_c = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            total_p = res_c.count if res_c.count else 0
            
            st.write(f"📊 Inventario: {total_p} / {limite} productos")
            st.progress(min(total_p / limite, 1.0))
            st.divider()

            # Gestión de Contenido
            t_add, t_inv, t_pay = st.tabs(["➕ AGREGAR", "📦 GESTIONAR", "💳 PAGOS"])

            with t_pay:
                nuevo_pago = st.text_input("Datos de Pago (Banco, Teléfono, etc.)", value=str(perf.get('datos_pago', '')))
                if st.button("💾 Guardar Datos"):
                    supabase.table("perfiles_comercio").update({"datos_pago": nuevo_pago}).eq("id", perf['id']).execute()
                    st.success("Guardado.")

            with t_add:
                if total_p >= limite:
                    st.error("Límite de plan alcanzado. ¡Sube de nivel para publicar más!")
                else:
                    with st.form("new_p", clear_on_submit=True):
                        n = st.text_input("Nombre")
                        p = st.number_input("Precio ($)")
                        v = st.file_uploader("Video publicitario", type=['mp4', 'mov'])
                        if st.form_submit_button("🚀 PUBLICAR"):
                            if n and v:
                                v_path = f"videos/{perf['id']}_{random.randint(1000,9999)}.mp4"
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
                        if st.button("🗑️ BORRAR", key=f"del_{i['id']}"):
                            supabase.table("productos").delete().eq("id", i['id']).execute()
                            st.rerun()
