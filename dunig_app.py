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

# Función para obtener datos bancarios desde Supabase (Blindaje)
def obtener_datos_pago():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "datos_bancarios").execute()
        if res.data:
            return res.data[0]['valor']
        return "⚠️ Datos de pago no configurados en el sistema."
    except Exception:
        return "❌ Error al cargar datos de pago."

# Función para mostrar video correctamente (Evita pantalla negra)
def renderizar_video(url_video):
    video_html = f"""
        <video width="100%" height="auto" autoplay muted loop playsinline style="border-radius: 10px; background-color: black;">
            <source src="{url_video}" type="video/mp4">
            Tu navegador no soporta el elemento de video.
        </video>
    """
    st.components.v1.html(video_html, height=300)

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
# 3. VISTA: REGISTRO INDIVIDUAL
# ==========================================
es_registro = st.query_params.get("reg") == "true"
es_admin = st.query_params.get("admin") == "true"

if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE NUEVO SOCIO</h1>", unsafe_allow_html=True)
    
    with st.container(border=True):
        st.markdown("### 💳 DATOS DE PAGO D'UNIG")
        st.info("Realiza el pago de tu plan y guarda la referencia para completar el registro.")
        
        banco_info = obtener_datos_pago()
        st.code(banco_info)
        
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
                    "nombre_comercio": rn, 
                    "email_propietario": rm, 
                    "whatsapp": rt,
                    "portada_url": url_i, 
                    "plan": plan_sel, 
                    "codigo_acceso": codigo_generado,
                    "pago_administrador_status": f"INICIAL REF: {ref_pago}"
                }).execute()
                
                ventana_bienvenida(rn, codigo_generado)
            else:
                st.error("Por favor rellena todos los campos e incluye la referencia de pago.")

# ==========================================
# 4. VISTA: PANEL DE CONTROL
# ==========================================
elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.container(border=True):
            m = st.text_input("Email").strip().lower()
            c = st.text_input("Código", type="password").strip().upper()
            if st.button("🔓 ENTRAR"):
                if m == st.secrets["ADMIN_EMAIL"] and c == st.secrets["ADMIN_PASS"]:
                    st.session_state.logged_in = True
                    st.session_state.is_super_admin = True
                    st.session_state.user_email = m
                    st.rerun()
                
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == c:
                    st.session_state.logged_in = True
                    st.session_state.user_email = m
                    st.rerun()
                else:
                    st.error("Acceso denegado")
    else:
        res_p = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        
        if res_p.data or st.session_state.is_super_admin:
            perf = res_p.data[0] if res_p.data else {"nombre_comercio": "ADMIN"}
            
            pestañas = ["➕ AGREGAR", "📦 GESTIÓN", "💳 MIS COBROS"]
            if st.session_state.is_super_admin:
                pestañas.append("👑 ADMIN GLOBAL")
            
            t = st.tabs(pestañas)

            with t[0]: # AGREGAR
                with st.form("add_p"):
                    nom = st.text_input("Nombre del Producto")
                    pre = st.number_input("Precio ($)")
                    vid = st.file_uploader("Video", type=['mp4'])
                    if st.form_submit_button("PUBLICAR"):
                        if nom and vid:
                            path = f"v/{random.randint(100,999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(path, vid.getvalue())
                            url = supabase.storage.from_("fotos_productos").get_public_url(path)
                            supabase.table("productos").insert({
                                "nombre_producto": nom, 
                                "precio": pre, 
                                "video_url": url, 
                                "comercio_relacionado": perf['nombre_comercio']
                            }).execute()
                            st.success("¡Producto publicado!"); st.rerun()

            with t[1]: # GESTIÓN (Donde se ven los videos)
                prods = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for pg in prods.data:
                    with st.container(border=True):
                        col_vid, col_info = st.columns([1, 1])
                        with col_vid:
                            # Aplicamos la función para evitar el cuadro negro
                            renderizar_video(pg['video_url'])
                        with col_info:
                            st.write(f"**{pg['nombre_producto']}**")
                            st.write(f"Precio: ${pg['precio']}")
                            if st.button("✏️ Editar", key=f"e_{pg['id']}"): editar_producto(pg)
                            if st.button("🗑️ Eliminar", key=f"d_{pg['id']}"):
                                supabase.table("productos").delete().eq("id", pg['id']).execute()
                                st.rerun()

            with t[2]: # COBROS
                db = st.text_area("Instrucciones de pago para tus clientes", value=perf.get('datos_pago', ''))
                if st.button("GUARDAR DATOS"):
                    supabase.table("perfiles_comercio").update({"datos_pago": db}).eq("id", perf['id']).execute()
                    st.success("Información actualizada")

            if st.session_state.is_super_admin:
                with t[3]: # ADMIN GLOBAL
                    st.subheader("🛠️ Control Maestro de Afiliados")
                    todos = supabase.table("perfiles_comercio").select("*").execute()
                    for tc in todos.data:
                        with st.container(border=True):
                            st.write(f"**Tienda:** {tc['nombre_comercio']} | **Plan:** {tc['plan']}")
                            st.caption(f"📢 Referencia de Registro: {tc.get('pago_administrador_status', 'N/A')}")
                            if st.button("ELIMINAR COMERCIO", key=f"del_m_{tc['id']}", type="primary"):
                                supabase.table("perfiles_comercio").delete().eq("id", tc['id']).execute()
                                st.rerun()

        if st.button("🚪 CERRAR SESIÓN"):
            st.session_state.logged_in = False
            st.session_state.is_super_admin = False
            st.session_state.user_email = None
            st.rerun()