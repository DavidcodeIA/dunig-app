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

PLANES = {
    "GRATUITO": {"cupos": 3, "precio": "Gratis", "beneficios": "Acceso básico, 3 productos, soporte estándar."},
    "BRONCE": {"cupos": 10, "precio": "$10/mes", "beneficios": "10 productos, etiqueta destacada, soporte prioritario."},
    "PLATA": {"cupos": 25, "precio": "$20/mes", "beneficios": "25 productos, analíticas básicas, personalización de colores."},
    "ORO": {"cupos": 9999, "precio": "$50/mes", "beneficios": "Productos ilimitados, gestión de pedidos avanzada, máxima visibilidad."}
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'is_super_admin' not in st.session_state: st.session_state.is_super_admin = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. DIÁLOGOS ESPECIALES
# ==========================================
@st.dialog("🙏 BIENVENIDO A LA FAMILIA D'UNIG")
def bienvenida_espiritual(nombre, codigo):
    st.markdown(f"### ✨ ¡Gloria a Dios, {nombre}!")
    st.write("Tu comercio ha sido registrado bajo la bendición del Altísimo.")
    st.success(f"**TU CÓDIGO DE ACCESO ES:** `{codigo}`")
    st.info("📌 *'Encomienda a Jehová tu camino, y confía en él; y él hará.' - Salmo 37:5*")
    st.warning("Guarda este código, lo necesitarás para gestionar tu tienda.")
    if st.button("ENTENDIDO"): st.rerun()

@st.dialog("✏️ EDITAR COMERCIO (MASTER)")
def editar_comercio_master(comercio):
    n = st.text_input("Nombre", value=comercio['nombre_comercio'])
    p = st.selectbox("Plan", list(PLANES.keys()), index=list(PLANES.keys()).index(comercio['plan']))
    if st.button("GUARDAR CAMBIOS"):
        supabase.table("perfiles_comercio").update({"nombre_comercio": n, "plan": p}).eq("id", comercio['id']).execute()
        st.success("Actualizado"); st.rerun()

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO ---
if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ UNIRSE A D'UNIG LUXURY</h1>", unsafe_allow_html=True)
    
    # Tabla de Beneficios
    with st.expander("💎 VER BENEFICIOS DE LOS PLANES"):
        for p, info in PLANES.items():
            st.markdown(f"**Plan {p} ({info['precio']}):** {info['beneficios']}")

    with st.form("form_reg_externo", clear_on_submit=True):
        rn = st.text_input("Nombre de la Tienda")
        rm = st.text_input("Email")
        rt = st.text_input("WhatsApp")
        plan_sel = st.selectbox("Selecciona tu Plan", list(PLANES.keys()))
        ri = st.file_uploader("Foto de Portada", type=['jpg', 'png'])
        ref_s = st.text_input("Referencia de Pago")
        if st.form_submit_button("REGISTRAR COMERCIO"):
            if rn and rm and rt and ri and ref_s:
                # Generar código único
                nuevo_codigo = f"LUX-{random.randint(1000, 9999)}"
                path_i = f"portadas/{random.randint(1000,9999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path_i, ri.getvalue())
                url_i = supabase.storage.from_("fotos_productos").get_public_url(path_i)
                
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": rn, "email_propietario": rm.lower(), "whatsapp": rt, 
                    "portada_url": url_i, "plan": plan_sel, "codigo_acceso": nuevo_codigo
                }).execute()
                
                bienvenida_espiritual(rn, nuevo_codigo)

# --- VISTA: PANEL CONTROL (ADMIN) ---
elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.container(border=True):
            m = st.text_input("Email").strip().lower()
            c = st.text_input("Código de Acceso", type="password").strip().upper()
            if st.button("🔓 ENTRAR"):
                # VALIDACIÓN MAESTRA (Protegida en Secrets)
                if m == st.secrets.get("ADMIN_EMAIL") and c == st.secrets.get("ADMIN_PASS"):
                    st.session_state.logged_in = True
                    st.session_state.is_super_admin = True
                    st.session_state.user_email = m
                    st.rerun()
                
                # VALIDACIÓN SOCIOS
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == c:
                    st.session_state.logged_in = True
                    st.session_state.is_super_admin = False
                    st.session_state.user_email = m
                    st.rerun()
                else: st.error("Acceso denegado")
    else:
        # Pestañas Dinámicas
        pestanas = ["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS"]
        if st.session_state.is_super_admin: pestanas.append("👑 ADMIN GLOBAL")
        
        t_list = st.tabs(pestanas)
        
        # Lógica para comercios normales (y tu propia tienda si quieres)
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        if res.data or st.session_state.is_super_admin:
            # Aquí va tu código de gestión de productos normal...
            with t_list[0]: st.write("Sección para subir productos...")
            
            # EXTENSIÓN MASTER (Solo tú)
            if st.session_state.is_super_admin:
                with t_list[-1]:
                    st.subheader("🛠️ CONTROL TOTAL DE COMERCIOS")
                    todos = supabase.table("perfiles_comercio").select("*").execute()
                    for tienda in todos.data:
                        with st.expander(f"🏪 {tienda['nombre_comercio']}"):
                            st.write(f"Email: {tienda['email_propietario']} | Plan: {tienda['plan']}")
                            col_e, col_d = st.columns(2)
                            if col_e.button("EDITAR", key=f"ed_{tienda['id']}"): editar_comercio_master(tienda)
                            if col_d.button("ELIMINAR", key=f"del_{tienda['id']}", type="primary"):
                                supabase.table("perfiles_comercio").delete().eq("id", tienda['id']).execute()
                                st.rerun()

# --- VISTA: MALL (POR DEFECTO) ---
else:
    # (Tu código de Mall que ya tienes arriba se mantiene aquí)
    st.write("Bienvenido al Mall...")