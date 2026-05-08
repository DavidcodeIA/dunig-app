import streamlit as st
from supabase import create_client, Client
import random

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="wide")

@st.cache_resource
def init_connection():
    # Asegúrate de tener SUPABASE_URL y SUPABASE_KEY en tus Secrets
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# BLINDAJE: Carga datos de pago desde la base de datos
def obtener_datos_pago():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "datos_bancarios").execute()
        return res.data[0]['valor'] if res.data else "⚠️ Datos no configurados."
    except:
        return "❌ Error de conexión."

# Inicialización de sesión
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'is_super_admin' not in st.session_state: st.session_state.is_super_admin = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

# Parámetros de URL
es_reg = st.query_params.get("reg") == "true"
es_admin = st.query_params.get("admin") == "true"

# ==========================================
# 2. VISTA: EL MALL (VISTA POR DEFECTO)
# ==========================================
if not es_reg and not es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>💎 D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    
    # Obtenemos productos de Supabase
    res = supabase.table("productos").select("*").execute()
    
    if res.data:
        cols = st.columns(2) # Optimizado para móvil
        for i, prod in enumerate(res.data):
            with cols[i % 2]:
                with st.container(border=True):
                    # Forzamos formato MP4 para evitar pantalla negra en móvil
                    st.video(prod['video_url'], format="video/mp4")
                    st.subheader(prod['nombre_producto'])
                    st.write(f"💰 **Precio:** ${prod['precio']}")
                    st.caption(f"🏪 {prod['comercio_relacionado']}")
                    
                    # Link dinámico a WhatsApp
                    ws_num = "584120000000" # Cambia por el número real o tráelo de la tabla perfiles
                    st.markdown(f"[📩 Contactar Vendedor](https://wa.me/{ws_num})")
    else:
        st.info("No hay productos disponibles en este momento.")

# ==========================================
# 3. VISTA: REGISTRO DE SOCIOS (?reg=true)
# ==========================================
elif es_reg:
    st.markdown("<h1 style='text-align:center;'>✨ REGISTRO DE SOCIO</h1>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("### 💳 DATOS DE PAGO")
        st.code(obtener_datos_pago()) # Blindaje activo
    
    with st.form("registro_socio"):
        nombre = st.text_input("Nombre de la Tienda")
        correo = st.text_input("Email").lower()
        ws = st.text_input("WhatsApp")
        foto = st.file_uploader("Foto Portada", type=['jpg', 'png'])
        ref = st.text_input("Referencia de Pago")
        
        if st.form_submit_button("COMPLETAR REGISTRO"):
            if nombre and correo and foto and ref:
                cod_acceso = f"LUX-{random.randint(1000, 9999)}"
                path = f"portadas/{random.randint(100,999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path, foto.getvalue())
                url_foto = supabase.storage.from_("fotos_productos").get_public_url(path)
                
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": nombre, "email_propietario": correo, 
                    "whatsapp": ws, "portada_url": url_foto, "codigo_acceso": cod_acceso,
                    "pago_administrador_status": f"REF: {ref}"
                }).execute()
                st.success(f"¡Bienvenido! Tu código es: {cod_acceso}")
            else:
                st.error("Faltan datos.")

# ==========================================
# 4. VISTA: PANEL DE CONTROL (?admin=true)
# ==========================================
elif es_admin:
    st.markdown("<h1 style='text-align:center;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.form("login"):
            u = st.text_input("Email").lower()
            p = st.text_input("Código", type="password").upper()
            if st.form_submit_button("ENTRAR"):
                # Login Super Admin (Secrets)
                if u == st.secrets["ADMIN_EMAIL"] and p == st.secrets["ADMIN_PASS"]:
                    st.session_state.logged_in = True
                    st.session_state.is_super_admin = True
                    st.session_state.user_email = u
                    st.rerun()
                # Login Socio
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", u).execute()
                if res.data and str(res.data[0]['codigo_acceso']).upper() == p:
                    st.session_state.logged_in = True
                    st.session_state.user_email = u
                    st.rerun()
                else:
                    st.error("Acceso denegado.")
    else:
        # Menú de gestión
        res_p = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        perf = res_p.data[0] if res_p.data else {"nombre_comercio": "ADMIN"}
        
        t1, t2 = st.tabs(["➕ SUBIR", "📦 GESTIONAR"])
        
        with t1:
            with st.form("upload_form"):
                n_prod = st.text_input("Nombre del Producto")
                p_prod = st.number_input("Precio")
                v_prod = st.file_uploader("Video MP4", type=['mp4'])
                if st.form_submit_button("PUBLICAR"):
                    if n_prod and v_prod:
                        path_v = f"v/{random.randint(1000,9999)}.mp4"
                        # IMPORTANTE: Forzamos el tipo de contenido para móviles
                        supabase.storage.from_("fotos_productos").upload(path_v, v_prod.getvalue(), {"content-type": "video/mp4"})
                        url_v = supabase.storage.from_("fotos_productos").get_public_url(path_v)
                        supabase.table("productos").insert({
                            "nombre_producto": n_prod, "precio": p_prod, 
                            "video_url": url_v, "comercio_relacionado": perf['nombre_comercio']
                        }).execute()
                        st.success("¡Publicado!"); st.rerun()

        with t2:
            items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            for it in items.data:
                with st.container(border=True):
                    st.video(it['video_url'])
                    st.write(f"**{it['nombre_producto']}**")
                    if st.button("🗑️ Eliminar", key=it['id']):
                        supabase.table("productos").delete().eq("id", it['id']).execute()
                        st.rerun()

        if st.button("Cerrar Sesión"):
            st.session_state.logged_in = False
            st.rerun()