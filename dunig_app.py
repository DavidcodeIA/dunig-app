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

PLANES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}
OPCIONES_PLAN_VISUAL = {
    "GRATUITO": "⚪ GRATUITO (3 Prods)",
    "BRONCE": "🥉 BRONCE (10 Prods)",
    "PLATA": "🥈 PLATA (25 Prods)",
    "ORO": "👑 ORO (Ilimitado)"
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA (3 COLUMNAS MÓVIL + OVALADO)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    [data-testid="stHorizontalBlock"] { display: flex; flex-direction: row !important; flex-wrap: nowrap !important; gap: 5px !important; }
    [data-testid="stHorizontalBlock"] > div { width: 33% !important; min-width: 33% !important; }
    .img-mall-luxury {
        width: 100%; aspect-ratio: 2 / 3; object-fit: cover;
        border-radius: 15px; border: 1px solid #D4AF37;
    }
    .tienda-nombre { color: #D4AF37; font-size: 9px; font-weight: bold; text-align: center; margin-top: 4px; text-transform: uppercase; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .stButton>button { background: linear-gradient(180deg, #D4AF37, #8A6E2F) !important; color: black !important; font-size: 9px !important; height: 22px !important; border-radius: 10px !important; border: none !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. FUNCIONES DE GESTIÓN (BORRADO CORREGIDO)
# ==========================================
def borrar_comercio_definitivo(c_id, c_nombre):
    try:
        # Intentamos borrar el comercio (si el SQL del Paso 1 está bien, borrará productos solo)
        res = supabase.table("perfiles_comercio").delete().eq("id", c_id).execute()
        st.toast(f"✅ {c_nombre} eliminado")
        st.rerun()
    except Exception as e:
        # Si falla, te mostraré el error real aquí abajo
        st.error(f"❌ Error al borrar: {str(e)}")

@st.dialog("📝 EDITAR")
def editar_dialog(c):
    n_w = st.text_input("WhatsApp", value=c['whatsapp'])
    n_p = st.selectbox("Plan", options=list(PLANES.keys()), index=list(PLANES.keys()).index(c.get('plan', 'GRATUITO')))
    if st.button("GUARDAR"):
        supabase.table("perfiles_comercio").update({"whatsapp": n_w, "plan": n_p}).eq("id", c['id']).execute()
        st.rerun()

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_reg = st.query_params.get("reg") == "true"

if es_reg:
    st.markdown("<h2 style='color:#D4AF37;'>REGISTRO</h2>", unsafe_allow_html=True)
    with st.form("reg"):
        rn = st.text_input("Tienda")
        rm = st.text_input("Email")
        rt = st.text_input("WhatsApp")
        ri = st.file_uploader("Portada", type=['jpg', 'png'])
        if st.form_submit_button("REGISTRAR"):
            if rn and ri:
                path = f"p/{random.randint(1000,9999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path, ri.getvalue())
                url = supabase.storage.from_("fotos_productos").get_public_url(path)
                supabase.table("perfiles_comercio").insert({"nombre_comercio":rn, "email_propietario":rm, "whatsapp":rt, "portada_url":url, "codigo_acceso":str(random.randint(1000,9999))}).execute()
                st.success("¡Listo!")

elif not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h4 style='text-align:center; color:#D4AF37;'>D'UNIG LUXURY MALL</h4>", unsafe_allow_html=True)
        tiendas = supabase.table("perfiles_comercio").select("*").execute().data
        for i in range(0, len(tiendas), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.markdown(f'<img src="{t.get("portada_url")}" class="img-mall-luxury">', unsafe_allow_html=True)
                        st.markdown(f'<div class="tienda-nombre">{t["nombre_comercio"]}</div>', unsafe_allow_html=True)
                        if st.button("VER", key=f"v_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')
    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER"): ir_a('mall')
        st.header(t['nombre_comercio'])
        # (Aquí va tu lógica de productos que ya funciona...)

else: # PANEL ADMIN / GESTIÓN DE COMERCIOS
    st.markdown("<h2 style='color:#D4AF37;'>⚙️ ADMINISTRACIÓN</h2>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        log_e = st.text_input("Email")
        log_p = st.text_input("Código", type="password")
        if st.button("ENTRAR"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", log_e).execute()
            if res.data and str(res.data[0]['codigo_acceso']) == log_p:
                st.session_state.logged_in = True; st.session_state.user_email = log_e; st.rerun()
    else:
        t1, t2 = st.tabs(["📦 MIS PRODUCTOS", "🏙️ TODOS LOS COMERCIOS"])
        
        with t1:
            st.write("Gestiona tus productos aquí...")
            if st.button("CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()

        with t2:
            st.subheader("Lista Maestra de Comercios")
            todos = supabase.table("perfiles_comercio").select("*").execute().data
            for c in todos:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([1, 2, 1, 1])
                    if c.get('portada_url'): c1.image(c['portada_url'], width=50)
                    c2.write(f"**{c['nombre_comercio']}**\n{c.get('plan','S/N')}")
                    if c3.button("📝", key=f"ed_{c['id']}"): editar_dialog(c)
                    
                    # BOTÓN DE BORRAR DEFINITIVO
                    if c4.button("🗑️", key=f"del_{c['id']}"):
                        borrar_comercio_definitivo(c['id'], c['nombre_comercio'])