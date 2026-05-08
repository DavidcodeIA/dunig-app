import streamlit as st
from supabase import create_client, Client
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

# Función para obtener datos bancarios (Blindaje para que no estén en el código)
def obtener_datos_pago():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "datos_bancarios").execute()
        return res.data[0]['valor'] if res.data else "⚠️ Datos de pago no configurados."
    except:
        return "❌ Error al cargar datos bancarios."

PLANES_INFO = {
    "GRATUITO": "✨ 3 Productos | Soporte Básico | Visibilidad Estándar",
    "BRONCE": "🥉 10 Productos | Etiqueta Bronce | Soporte Prioritario ($10)",
    "PLATA": "🥈 25 Productos | Etiqueta Plata | Analíticas ($20)",
    "ORO": "🥇 Productos Ilimitados | Gestión VIP ($50)"
}

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_super_admin' not in st.session_state: st.session_state.is_super_admin = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

# ==========================================
# 2. DIÁLOGOS
# ==========================================
@st.dialog("🙏 ¡BIENVENIDO A D'UNIG!")
def ventana_bienvenida(nombre, codigo):
    st.markdown(f"### ✨ ¡Bendiciones, {nombre}!")
    st.write("Tu comercio ha sido registrado. Dios bendiga tu emprendimiento.")
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
# 3. VISTA: REGISTRO (CON DATOS BANCARIOS BLINDADOS)
# ==========================================
es_registro = st.query_params.get("reg") == "true"
es_admin = st.query_params.get("admin") == "true"

if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE NUEVO SOCIO</h1>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### 💳 DATOS DE PAGO D'UNIG")
        st.info("Realiza el pago de tu plan y guarda la referencia.")
        
        # Datos desde Supabase, no escritos aquí
        st.code(obtener_datos_pago())
        
        st.markdown("#### 💎 BENEFICIOS POR PLAN")
        for p, desc in PLANES_INFO.items():
            st.write(f"**Plan {p}:** {desc}")

    with st.form("form_registro_socio", clear_on_submit=True):
        rn = st.text_input("Nombre de la Tienda")
        rm = st.text_input("Email").lower()
        rt = st.text_input("WhatsApp (Ej: 58412...)")
        plan_sel = st.selectbox("Selecciona tu Plan", list(PLANES_INFO.keys()))
        ri = st.file_uploader("Foto de Portada", type=['jpg', 'png'])
        ref_pago = st.text_input("Referencia de Pago (Obligatorio)")
        
        if st.form_submit_button("FINALIZAR REGISTRO"):
            if rn and rm and rt and ri and ref_pago:
                codigo_generado = f"LUX-{random.randint(1000, 9999)}"
                path_i = f"portadas/tienda_{random.randint(100,999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path_i, ri.getvalue())
                url_i = supabase.storage.from_("fotos_productos").get_public_url(path_i)
                
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": rn, "email_propietario": rm, "whatsapp": rt,
                    "portada_url": url_i, "plan": plan_sel, "codigo_acceso": codigo_generado,
                    "pago_administrador_status": f"INICIAL REF: {ref_pago}"
                }).execute()
                
                ventana_bienvenida(rn, codigo_generado)
            else:
                st.error("Rellena todos los campos e incluye la referencia.")

# ==========================================
# 4. VISTA: PANEL DE CONTROL (CON VISTA DE VIDEO DIRECTA)
# ==========================================
elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.container(border=True):
            m = st.text_input("Email").strip().lower()
            c = st.text_input("Código", type="password").strip().upper()
            if st.button("🔓 ENTRAR"):
                if m == st.secrets["ADMIN_EMAIL"] and c == st.secrets["ADMIN_PASS"]:
                    st.session_state.logged_in = True; st.session_state.is_super_admin = True
                    st.session_state.user_email = m; st.rerun()
                
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == c:
                    st.session_state.logged_in = True; st.session_state.user_email = m; st.rerun()
                else: st.error("Acceso denegado")
    else:
        res_p = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        
        if res_p.data or st.session_state.is_super_admin:
            perf = res_p.data[0] if res_p.data else {"nombre_comercio": "ADMIN"}
            pestañas = ["➕ AGREGAR", "📦 GESTIÓN", "💳 MIS COBROS"]
            if st.session_state.is_super_admin: pestañas.append("👑 ADMIN GLOBAL")
            t = st.tabs(pestañas)

            with t[0]: # AGREGAR PRODUCTO
                with st.form("add_p"):
                    nom = st.text_input("Nombre del Producto")
                    pre = st.number_input("Precio ($)")
                    vid = st.file_uploader("Video", type=['mp4'])
                    if st.form_submit_button("PUBLICAR"):
                        if nom and vid:
                            path = f"v/{random.randint(100,999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(path, vid.getvalue())
                            url = supabase.storage.from_("fotos_productos").get_public_url(path)
                            supabase.table("productos").insert({"nombre_producto": nom, "precio": pre, "video_url": url, "comercio_relacionado": perf['nombre_comercio']}).execute()
                            st.success("¡Publicado!"); st.rerun()

            with t[1]: # GESTIÓN (RESTAURADO PARA VER VIDEOS)
                prods = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for pg in prods.data:
                    with st.container(border=True):
                        st.video(pg['video_url']) # Método directo que siempre te funcionó
                        st.write(f"**{pg['nombre_producto']}** | ${pg['precio']}")
                        c1, c2 = st.columns(2)
                        if c1.button("✏️", key=f"e_{pg['id']}"): editar_producto(pg)
                        if c2.button("🗑️", key=f"d_{pg['id']}"):
                            supabase.table("productos").delete().eq("id", pg['id']).execute(); st.rerun()

            with t[2]: # COBROS DEL COMERCIO
                db = st.text_area("Instrucciones de pago para tus clientes", value=perf.get('datos_pago', ''))
                if st.button("GUARDAR DATOS"):
                    supabase.table("perfiles_comercio").update({"datos_pago": db}).eq("id", perf['id']).execute()
                    st.success("Ok")

            if st.session_state.is_super_admin:
                with t[3]: # ADMIN GLOBAL
                    todos = supabase.table("perfiles_comercio").select("*").execute()
                    for tc in todos.data:
                        with st.container(border=True):
                            st.write(f"**{tc['nombre_comercio']}** | {tc['plan']}")
                            st.caption(f"Ref Pago: {tc.get('pago_administrador_status')}")
                            if st.button("ELIMINAR", key=f"del_m_{tc['id']}"):
                                supabase.table("perfiles_comercio").delete().eq("id", tc['id']).execute(); st.rerun()

        if st.button("🚪 CERRAR SESIÓN"):
            st.session_state.logged_in = False; st.rerun()