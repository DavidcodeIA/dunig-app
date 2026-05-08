import streamlit as st
from supabase import create_client, Client
import random

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY ADMIN", layout="centered")

@st.cache_resource
def init_connection():
    # Estas claves deben estar en Settings > Secrets de Streamlit
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# FUNCIÓN DE BLINDAJE: Carga datos desde Supabase, no del código
def obtener_datos_pago():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "datos_bancarios").execute()
        return res.data[0]['valor'] if res.data else "⚠️ Datos de pago no configurados."
    except:
        return "❌ Error de conexión."

PLANES_INFO = {
    "GRATUITO": "✨ 3 Productos | Soporte Básico",
    "BRONCE": "🥉 10 Productos | Soporte Prioritario ($10)",
    "PLATA": "🥈 25 Productos | Analíticas ($20)",
    "ORO": "🥇 Productos Ilimitados | Gestión VIP ($50)"
}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_super_admin' not in st.session_state: st.session_state.is_super_admin = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

# ==========================================
# 2. DIÁLOGOS (POP-UPS)
# ==========================================
@st.dialog("🙏 ¡BIENVENIDO!")
def ventana_bienvenida(nombre, codigo):
    st.markdown(f"### ✨ ¡Bendiciones, {nombre}!")
    st.write("Registro completado con éxito.")
    st.success(f"**TU CÓDIGO DE ACCESO:** `{codigo}`")
    st.info("📌 *Salmo 37:5*")
    if st.button("ENTRAR AL PANEL"): st.rerun()

@st.dialog("✏️ EDITAR")
def editar_producto(prod):
    nuevo_nom = st.text_input("Nombre", value=prod['nombre_producto'])
    nuevo_pre = st.number_input("Precio ($)", value=float(prod['precio']))
    if st.button("ACTUALIZAR"):
        supabase.table("productos").update({"nombre_producto": nuevo_nom, "precio": nuevo_pre}).eq("id", prod['id']).execute()
        st.rerun()

# ==========================================
# 3. LÓGICA DE NAVEGACIÓN
# ==========================================
es_registro = st.query_params.get("reg") == "true"
es_admin = st.query_params.get("admin") == "true"

# --- VISTA: REGISTRO ---
if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO D'UNIG</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### 💳 DATOS PARA EL PAGO")
        st.code(obtener_datos_pago()) # Blindaje activo
    
    with st.form("form_reg"):
        rn = st.text_input("Nombre Tienda")
        rm = st.text_input("Email").lower()
        rt = st.text_input("WhatsApp")
        pl = st.selectbox("Plan", list(PLANES_INFO.keys()))
        fp = st.file_uploader("Portada", type=['jpg', 'png'])
        ref = st.text_input("Referencia de Pago")
        if st.form_submit_button("REGISTRAR"):
            if rn and rm and fp and ref:
                cod = f"LUX-{random.randint(1000, 9999)}"
                path = f"portadas/{random.randint(100,999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path, fp.getvalue())
                url_f = supabase.storage.from_("fotos_productos").get_public_url(path)
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": rn, "email_propietario": rm, "whatsapp": rt,
                    "portada_url": url_f, "plan": pl, "codigo_acceso": cod,
                    "pago_administrador_status": f"REF: {ref}"
                }).execute()
                ventana_bienvenida(rn, cod)

# --- VISTA: PANEL ---
elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ ADMINISTRACIÓN</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.form("login"):
            u = st.text_input("Email").lower()
            p = st.text_input("Código", type="password").upper()
            if st.form_submit_button("🔓 ACCEDER"):
                if u == st.secrets["ADMIN_EMAIL"] and p == st.secrets["ADMIN_PASS"]:
                    st.session_state.logged_in = True; st.session_state.is_super_admin = True
                    st.session_state.user_email = u; st.rerun()
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", u).execute()
                if res.data and str(res.data[0]['codigo_acceso']).upper() == p:
                    st.session_state.logged_in = True; st.session_state.user_email = u; st.rerun()
                else: st.error("Acceso incorrecto")
    else:
        # Panel activo
        res_p = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        perf = res_p.data[0] if res_p.data else {"nombre_comercio": "ADMIN"}
        
        t = st.tabs(["➕ SUBIR", "📦 GESTIÓN", "💳 COBROS", "👑 MASTER"])
        
        with t[0]: # SUBIR PRODUCTO
            with st.form("add"):
                nom = st.text_input("Producto")
                pre = st.number_input("Precio")
                vid = st.file_uploader("Video", type=['mp4'])
                if st.form_submit_button("PUBLICAR"):
                    if nom and vid:
                        path_v = f"v/{random.randint(1000,9999)}.mp4"
                        # ESTO EVITA LA PANTALLA NEGRA: Forzar el tipo de archivo
                        supabase.storage.from_("fotos_productos").upload(path_v, vid.getvalue(), {"content-type": "video/mp4"})
                        url_v = supabase.storage.from_("fotos_productos").get_public_url(path_v)
                        supabase.table("productos").insert({"nombre_producto": nom, "precio": pre, "video_url": url_v, "comercio_relacionado": perf['nombre_comercio']}).execute()
                        st.success("Listo"); st.rerun()

        with t[1]: # GESTIÓN DE PRODUCTOS
            prods = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            for pg in prods.data:
                with st.container(border=True):
                    st.video(pg['video_url']) # Carga directa
                    st.write(f"**{pg['nombre_producto']}**")
                    c1, c2 = st.columns(2)
                    if c1.button("✏️", key=f"e_{pg['id']}"): editar_producto(pg)
                    if c2.button("🗑️", key=f"d_{pg['id']}"):
                        supabase.table("productos").delete().eq("id", pg['id']).execute(); st.rerun()

        with t[2]: # DATOS DE COBRO
            db = st.text_area("Tus datos para clientes", value=perf.get('datos_pago', ''))
            if st.button("GUARDAR"):
                supabase.table("perfiles_comercio").update({"datos_pago": db}).eq("id", perf['id']).execute()
                st.success("Actualizado")

        with t[3]: # SOLO MASTER ADMIN
            if st.session_state.is_super_admin:
                todos = supabase.table("perfiles_comercio").select("*").execute()
                for tc in todos.data:
                    st.write(f"{tc['nombre_comercio']} - Ref: {tc.get('pago_administrador_status')}")
                    if st.button("ELIMINAR", key=f"m_{tc['id']}"):
                        supabase.table("perfiles_comercio").delete().eq("id", tc['id']).execute(); st.rerun()
            else: st.warning("Área restringida.")

        if st.button("🚪 SALIR"):
            st.session_state.logged_in = False; st.rerun()
else:
    st.info("⚠️ Acceso restringido. Usa la URL correspondiente.")