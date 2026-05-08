import streamlit as st
from supabase import create_client, Client
import random

# ==========================================
# 1. CONFIGURACIÓN INICIAL
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY ADMIN", layout="centered")

@st.cache_resource
def init_connection():
    # Asegúrate de tener estas claves en los "Secrets" de Streamlit
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# FUNCIÓN MAESTRA: Obtiene tus datos bancarios de Supabase (Blindaje)
def obtener_datos_pago():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "datos_bancarios").execute()
        if res.data:
            return res.data[0]['valor']
        return "⚠️ Configura 'datos_bancarios' en la tabla 'ajustes_sistema'."
    except Exception:
        return "❌ Error de conexión con los datos de pago."

PLANES_INFO = {
    "GRATUITO": "✨ 3 Productos | Soporte Básico | Visibilidad Estándar",
    "BRONCE": "🥉 10 Productos | Etiqueta Bronce | Soporte Prioritario ($10)",
    "PLATA": "🥈 25 Productos | Etiqueta Plata | Analíticas ($20)",
    "ORO": "🥇 Productos Ilimitados | Gestión VIP ($50)"
}

# Inicializar estados de sesión
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_super_admin' not in st.session_state: st.session_state.is_super_admin = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

# ==========================================
# 2. DIÁLOGOS Y UTILIDADES
# ==========================================
@st.dialog("🙏 ¡BIENVENIDO A D'UNIG!")
def ventana_bienvenida(nombre, codigo):
    st.markdown(f"### ✨ ¡Bendiciones, {nombre}!")
    st.write("Tu comercio ha sido registrado con éxito.")
    st.success(f"**TU CÓDIGO DE ACCESO ES:** `{codigo}`")
    st.info("📌 *'Encomienda a Jehová tu camino, y confía en él; y él hará.' - Salmo 37:5*")
    if st.button("ENTRAR AL PANEL"): st.rerun()

@st.dialog("✏️ EDITAR PRODUCTO")
def editar_producto(prod):
    nuevo_nom = st.text_input("Nombre", value=prod['nombre_producto'])
    nuevo_pre = st.number_input("Precio ($)", value=float(prod['precio']))
    if st.button("ACTUALIZAR"):
        supabase.table("productos").update({"nombre_producto": nuevo_nom, "precio": nuevo_pre}).eq("id", prod['id']).execute()
        st.success("¡Actualizado!"); st.rerun()

# ==========================================
# 3. LÓGICA DE VISTAS (REG / ADMIN)
# ==========================================
es_registro = st.query_params.get("reg") == "true"
es_admin = st.query_params.get("admin") == "true"

# --- VISTA: REGISTRO DE SOCIOS ---
if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE SOCIO</h1>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### 💳 DATOS DE PAGO")
        st.info("Realiza tu pago y guarda la referencia.")
        # Aquí se muestran tus datos bancarios ocultos del código
        st.code(obtener_datos_pago())
        
        st.markdown("#### 💎 PLANES")
        for p, desc in PLANES_INFO.items():
            st.write(f"**{p}:** {desc}")

    with st.form("form_registro", clear_on_submit=True):
        nombre_t = st.text_input("Nombre de la Tienda")
        email_t = st.text_input("Email").lower()
        whatsapp_t = st.text_input("WhatsApp (Ej: 58412...)")
        plan_sel = st.selectbox("Plan", list(PLANES_INFO.keys()))
        foto_p = st.file_uploader("Foto Portada", type=['jpg', 'png'])
        referencia = st.text_input("Referencia de Pago")
        
        if st.form_submit_button("REGISTRARME"):
            if nombre_t and email_t and whatsapp_t and foto_p and referencia:
                cod = f"LUX-{random.randint(1000, 9999)}"
                path = f"portadas/{random.randint(100,999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path, foto_p.getvalue())
                url_f = supabase.storage.from_("fotos_productos").get_public_url(path)
                
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": nombre_t, "email_propietario": email_t, 
                    "whatsapp": whatsapp_t, "portada_url": url_f, "plan": plan_sel, 
                    "codigo_acceso": cod, "pago_administrador_status": f"REF: {referencia}"
                }).execute()
                ventana_bienvenida(nombre_t, cod)
            else:
                st.error("Completa todos los campos.")

# --- VISTA: PANEL DE ADMINISTRACIÓN ---
elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.container(border=True):
            user_in = st.text_input("Email").strip().lower()
            pass_in = st.text_input("Código", type="password").strip().upper()
            if st.button("🔓 ENTRAR"):
                # Check Super Admin
                if user_in == st.secrets["ADMIN_EMAIL"] and pass_in == st.secrets["ADMIN_PASS"]:
                    st.session_state.logged_in = True; st.session_state.is_super_admin = True
                    st.session_state.user_email = user_in; st.rerun()
                
                # Check Socio
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", user_in).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == pass_in:
                    st.session_state.logged_in = True; st.session_state.user_email = user_in; st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    else:
        # Menú del Panel
        res_p = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        perf = res_p.data[0] if res_p.data else {"nombre_comercio": "ADMIN"}
        
        tabs = ["➕ AGREGAR", "📦 GESTIÓN", "💳 MIS COBROS"]
        if st.session_state.is_super_admin: tabs.append("👑 ADMIN GLOBAL")
        t = st.tabs(tabs)

        with t[0]: # AGREGAR
            with st.form("add_p"):
                n = st.text_input("Producto")
                p = st.number_input("Precio ($)")
                v = st.file_uploader("Video MP4", type=['mp4'])
                if st.form_submit_button("SUBIR"):
                    if n and v:
                        path_v = f"v/{random.randint(1000,9999)}.mp4"
                        # Forzamos el tipo de contenido para evitar pantalla negra en móvil
                        supabase.storage.from_("fotos_productos").upload(path_v, v.getvalue(), {"content-type": "video/mp4"})
                        url_v = supabase.storage.from_("fotos_productos").get_public_url(path_v)
                        supabase.table("productos").insert({
                            "nombre_producto": n, "precio": p, "video_url": url_v, 
                            "comercio_relacionado": perf['nombre_comercio']
                        }).execute()
                        st.success("Subido con éxito"); st.rerun()

        with t[1]: # GESTIÓN (REPARADO PARA MÓVIL)
            st.subheader("Tus Productos")
            prods = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            for pg in prods.data:
                with st.container(border=True):
                    # Usamos st.video nativo, que es lo más estable
                    st.video(pg['video_url'], format="video/mp4")
                    st.write(f"**{pg['nombre_producto']}** | ${pg['precio']}")
                    c1, c2 = st.columns(2)
                    if c1.button("✏️", key=f"edit_{pg['id']}"): editar_producto(pg)
                    if c2.button("🗑️", key=f"del_{pg['id']}"):
                        supabase.table("productos").delete().eq("id", pg['id']).execute(); st.rerun()

        with t[2]: # COBROS COMERCIO
            instruc = st.text_area("Instrucciones para tus clientes", value=perf.get('datos_pago', ''))
            if st.button("GUARDAR CONFIG"):
                supabase.table("perfiles_comercio").update({"datos_pago": instruc}).eq("id", perf['id']).execute()
                st.success("Guardado")

        if st.session_state.is_super_admin:
            with t[3]: # ADMIN GLOBAL
                st.subheader("Maestro de Comercios")
                todos = supabase.table("perfiles_comercio").select("*").execute()
                for tc in todos.data:
                    with st.container(border=True):
                        st.write(f"**{tc['nombre_comercio']}** | Plan: {tc['plan']}")
                        st.caption(f"Registro: {tc.get('pago_administrador_status')}")
                        if st.button("ELIMINAR SOCIO", key=f"global_del_{tc['id']}"):
                            supabase.table("perfiles_comercio").delete().eq("id", tc['id']).execute(); st.rerun()

        if st.button("🚪 CERRAR SESIÓN"):
            st.session_state.logged_in = False; st.rerun()

else:
    st.info("Usa ?admin=true para el panel o ?reg=true para registrarte.")