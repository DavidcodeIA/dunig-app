import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

PLANES = {"BRONCE": 5, "PLATINUM": 15, "DIAMANTE": 50}

# --- ESTADO DE SESIÓN ---
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

def generar_codigo():
    return ''.join(random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(7))

# ==========================================
# 2. ESTÉTICA LUXURY (CSS REFORZADO)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .luxury-card {
        background: rgba(255, 255, 255, 0.05); 
        border: 1px solid #D4AF37;
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(212, 175, 55, 0.1);
        border-radius: 10px 10px 0px 0px; color: white; padding: 10px;
    }
    .stTabs [aria-selected="true"] { background-color: #D4AF37 !important; color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE NAVEGACIÓN (ADMIN vs CLIENTE)
# ==========================================
es_admin = st.query_params.get("admin") == "true"

if not es_admin:
    # --- VISTA CLIENTE ---
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        res = supabase.table("perfiles_comercio").select("*").execute()
        cols = st.columns(2)
        for idx, t in enumerate(res.data):
            with cols[idx % 2]:
                with st.container(border=True):
                    if t.get('portada_url'): st.image(t['portada_url'])
                    st.subheader(t['nombre_comercio'].upper())
                    if st.button("VISITAR", key=f"btn_{t['id']}", use_container_width=True):
                        st.session_state.tienda_actual = t
                        ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
        if t.get('portada_url'): st.image(t['portada_url'], use_container_width=True)
        st.title(f"✨ {t['nombre_comercio']}")
        # (Aquí cargarías los productos igual que antes)

else:
    # --- PANEL DE CONTROL (ADMIN) ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)

    if not st.session_state.logged_in:
        # --- LOGIN ---
        with st.container(border=True):
            mail = st.text_input("Email registrado").strip().lower()
            code = st.text_input("Código de acceso", type="password").strip().upper()
            c1, c2 = st.columns(2)
            if c1.button("🔓 ENTRAR", use_container_width=True):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
                if res.data and str(res.data[0].get('codigo_acceso','')).upper() == code:
                    st.session_state.logged_in = True
                    st.session_state.user_email = mail
                    st.rerun()
                else: st.error("Datos incorrectos")
            if c2.button("🔑 PEDIR LLAVE", use_container_width=True):
                # (Lógica de WhatsApp ya conocida)
                pass
    else:
        # --- VISTA RECUPERADA DEL PANEL ---
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        if res.data:
            perf = res.data[0]
            st.success(f"Sesión activa: {perf['nombre_comercio']}")
            
            # Pestañas principales
            t1, t2, t3, t4, t5 = st.tabs(["➕ PRODUCTO", "📦 MI TIENDA", "🖼️ PORTADA", "💳 PAGOS", "✨ REGISTRO"])

            with t1:
                st.subheader("Subir Nuevo Producto")
                with st.form("add_p", clear_on_submit=True):
                    n = st.text_input("Nombre")
                    p = st.number_input("Precio ($)")
                    v = st.file_uploader("Video MP4", type=['mp4'])
                    if st.form_submit_button("PUBLICAR"):
                        # (Lógica de subida a Storage)
                        st.info("Procesando...")

            with t2:
                st.subheader("Gestión de Inventario")
                # Aquí listarías los productos con botón de eliminar

            with t3:
                st.subheader("Imagen de Portada")
                if perf.get('portada_url'): st.image(perf['portada_url'], width=200)
                new_img = st.file_uploader("Cambiar portada", type=['jpg','png'])
                if st.button("ACTUALIZAR IMAGEN"):
                    if new_img:
                        # Subir y actualizar en perfiles_comercio
                        st.success("Imagen actualizada")

            with t4:
                st.subheader("Datos de Cobro")
                datos = st.text_area("Instrucciones de pago", value=perf.get('datos_pago',''))
                if st.button("GUARDAR DATOS"):
                    supabase.table("perfiles_comercio").update({"datos_pago": datos}).eq("id", perf['id']).execute()
                    st.success("Datos guardados")

            with t5:
                st.subheader("Registrar Nuevo Miembro")
                with st.form("reg_admin"):
                    r_nom = st.text_input("Nombre Tienda")
                    r_mail = st.text_input("Email")
                    r_wa = st.text_input("WhatsApp")
                    if st.form_submit_button("CREAR CUENTA"):
                        # Insertar en Supabase
                        st.success("Socio registrado")

            if st.button("🚪 CERRAR SESIÓN"):
                st.session_state.logged_in = False
                st.rerun()