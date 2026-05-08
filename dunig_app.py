import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONEXIÓN Y CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY ADMIN", layout="centered")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

PLANES = {
    "GRATUITO": 3,
    "BRONCE": 10,
    "PLATA": 25,
    "ORO": 9999
}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_super_admin' not in st.session_state: st.session_state.is_super_admin = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

# ==========================================
# 2. FUNCIONES DE APOYO Y DIÁLOGOS
# ==========================================
@st.dialog("✏️ EDITAR PRODUCTO")
def editar_producto(prod):
    nuevo_nom = st.text_input("Nombre", value=prod['nombre_producto'])
    nuevo_pre = st.number_input("Precio ($)", value=float(prod['precio']))
    if st.button("ACTUALIZAR"):
        supabase.table("productos").update({"nombre_producto": nuevo_nom, "precio": nuevo_pre}).eq("id", prod['id']).execute()
        st.success("¡Actualizado!"); st.rerun()

@st.dialog("✏️ GESTIÓN MAESTRA (ADMIN)")
def editar_comercio_master(comercio):
    st.write(f"Editando: {comercio['nombre_comercio']}")
    nuevo_plan = st.selectbox("Cambiar Plan", list(PLANES.keys()), index=list(PLANES.keys()).index(comercio['plan']))
    if st.button("CONFIRMAR CAMBIO"):
        supabase.table("perfiles_comercio").update({"plan": nuevo_plan}).eq("id", comercio['id']).execute()
        st.success("Plan actualizado"); st.rerun()

# ==========================================
# 3. PANEL DE CONTROL (RESTAURADO)
# ==========================================
st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL D'UNIG</h1>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    with st.container(border=True):
        m = st.text_input("Email").strip().lower()
        c = st.text_input("Código de Acceso", type="password").strip().upper()
        
        if st.button("🔓 ENTRAR AL SISTEMA"):
            # A. Verificación de Súper Admin (vía Secrets)
            if m == st.secrets["ADMIN_EMAIL"] and c == st.secrets["ADMIN_PASS"]:
                st.session_state.logged_in = True
                st.session_state.is_super_admin = True
                st.session_state.user_email = m
                st.rerun()
            
            # B. Verificación de Comercio Normal
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
            if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == c:
                st.session_state.logged_in = True
                st.session_state.is_super_admin = False
                st.session_state.user_email = m
                st.rerun()
            else:
                st.error("Credenciales incorrectas.")

else:
    # Recuperar datos del perfil logueado
    res_p = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
    
    if res_p.data:
        perf = res_p.data[0]
        
        # Pestañas principales
        tabs = ["➕ AGREGAR", "📦 GESTIÓN", "💳 MIS COBROS", "💰 PAGO A D'UNIG"]
        if st.session_state.is_super_admin:
            tabs.append("👑 ADMIN GLOBAL")
            
        t_list = st.tabs(tabs)

        # --- PESTAÑA 1: AGREGAR (CARGA) ---
        with t_list[0]:
            st.subheader("Publicar nuevo producto")
            with st.form("form_add", clear_on_submit=True):
                n = st.text_input("Nombre del Producto")
                p = st.number_input("Precio ($)", min_value=0.0)
                v = st.file_uploader("Video publicitario (MP4)", type=['mp4'])
                if st.form_submit_button("PUBLICAR"):
                    if n and v:
                        path = f"v/{random.randint(1000,9999)}.mp4"
                        supabase.storage.from_("fotos_productos").upload(path, v.getvalue())
                        url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                        supabase.table("productos").insert({
                            "nombre_producto": n, "precio": p, "video_url": url_v, 
                            "comercio_relacionado": perf['nombre_comercio']
                        }).execute()
                        st.success("¡Producto en línea!"); st.rerun()

        # --- PESTAÑA 2: GESTIÓN ---
        with t_list[1]:
            st.subheader("Tus productos publicados")
            prods = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            for pg in prods.data:
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(pg['nombre_producto'])
                if col2.button("✏️", key=f"e_{pg['id']}"): editar_producto(pg)
                if col3.button("🗑️", key=f"d_{pg['id']}"):
                    supabase.table("productos").delete().eq("id", pg['id']).execute(); st.rerun()

        # --- PESTAÑA 3: MIS COBROS (Cómo le pagan al comercio) ---
        with t_list[2]:
            st.subheader("Configura cómo te pagan tus clientes")
            datos = st.text_area("Instrucciones de pago (Pago móvil, Zelle, etc.)", value=perf.get('datos_pago','') or "")
            if st.button("ACTUALIZAR DATOS DE COBRO"):
                supabase.table("perfiles_comercio").update({"datos_pago": datos}).eq("id", perf['id']).execute()
                st.success("Datos actualizados.")

        # --- PESTAÑA 4: PAGO A D'UNIG (Opción solicitada) ---
        with t_list[3]:
            st.subheader("Saldar cuenta con la administración")
            st.info("Utiliza los siguientes datos para pagar tu mensualidad o comisión:")
            st.code("TU_CUENTA_DE_PAGO_AQUÍ\nBanco: XYZ\nTitular: D'UNIG GLOBAL")
            
            ref_pago = st.text_input("Ingrese el número de referencia del pago enviado")
            if st.button("NOTIFICAR PAGO A ADMIN"):
                supabase.table("perfiles_comercio").update({"pago_administrador_status": f"REF: {ref_pago}"}).eq("id", perf['id']).execute()
                st.success("Pago notificado. El administrador lo revisará en breve.")

        # --- PESTAÑA 5: ADMIN GLOBAL (Solo tú) ---
        if st.session_state.is_super_admin:
            with t_list[4]:
                st.subheader("👑 Control Maestro de Comercios")
                todos = supabase.table("perfiles_comercio").select("*").execute()
                for com in todos.data:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        c1.write(f"**{com['nombre_comercio']}**\n{com['email_propietario']}\nPago: {com.get('pago_administrador_status', 'Pendiente')}")
                        if c2.button("GESTIONAR", key=f"m_ed_{com['id']}"): editar_comercio_master(com)
                        if c3.button("ELIMINAR", key=f"m_del_{com['id']}", type="primary"):
                            supabase.table("perfiles_comercio").delete().eq("id", com['id']).execute(); st.rerun()

    if st.button("🚪 CERRAR SESIÓN"):
        st.session_state.logged_in = False
        st.session_state.is_super_admin = False
        st.rerun()