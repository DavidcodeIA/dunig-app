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

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 30px !important;
        font-weight: 800 !important; text-transform: uppercase;
    }
    .img-redonda {
        width: 140px; height: 140px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 10px auto; display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VISTAS DE LA APP
# ==========================================
es_admin = st.query_params.get("admin") == "true"

if not es_admin:
    # --- VISTA MALL / TIENDA (IGUAL A LA ANTERIOR) ---
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        res = supabase.table("perfiles_comercio").select("*").execute()
        tiendas = res.data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        url = t.get('portada_url') or "https://via.placeholder.com/150"
                        st.markdown(f'<img src="{url}" class="img-redonda">', unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; color:#D4AF37; font-weight:bold;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                        if st.button("VISITAR", key=f"m_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ MALL"): ir_a('mall')
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        for p in prods.data:
            st.video(p['video_url'])
            st.markdown(f"<h3 style='text-align:center;'>{p['nombre_producto']} - ${p['precio']}</h3>", unsafe_allow_html=True)
            st.divider()

else:
    # --- PANEL ADMIN (CORREGIDO) ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.container(border=True):
            m = st.text_input("Email").strip().lower()
            c = st.text_input("Código", type="password").strip().upper()
            if st.button("🔓 ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == c:
                    st.session_state.logged_in = True; st.session_state.user_email = m; st.rerun()
                else: st.error("Acceso denegado")
    else:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        if res.data:
            perf = res.data[0]
            t1, t2, t3, t4 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS", "✨ REGISTRO"])
            
            with t1:
                with st.form("form_add", clear_on_submit=True):
                    nom_p = st.text_input("Nombre del Producto")
                    pre_p = st.number_input("Precio ($)", min_value=0.0)
                    vid_p = st.file_uploader("Video MP4", type=['mp4'])
                    if st.form_submit_button("PUBLICAR PRODUCTO"):
                        if nom_p and vid_p:
                            path = f"v/{random.randint(1000,9999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(path, vid_p.getvalue())
                            url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                            supabase.table("productos").insert({"nombre_producto":nom_p, "precio":pre_p, "video_url":url_v, "comercio_relacionado":perf['nombre_comercio']}).execute()
                            st.success("¡Producto en línea!"); st.rerun()

            with t2:
                st.subheader("Mi Perfil")
                st.markdown(f"**Tienda:** {perf['nombre_comercio']}")
                if perf.get('portada_url'): st.image(perf['portada_url'], width=100)
                
                # Aquí puse la edición de foto FUERA del formulario de registro
                nueva_f = st.file_uploader("Actualizar mi logo/portada", type=['jpg', 'png'])
                if st.button("ACTUALIZAR MI FOTO"):
                    if nueva_f:
                        path_i = f"portadas/p_{perf['id']}.jpg"
                        supabase.storage.from_("fotos_productos").upload(path_i, nueva_f.getvalue(), {"x-upsert": "true"})
                        url_i = supabase.storage.from_("fotos_productos").get_public_url(path_i)
                        supabase.table("perfiles_comercio").update({"portada_url": url_i}).eq("id", perf['id']).execute()
                        st.success("Foto actualizada"); st.rerun()

            with t3:
                st.subheader("Configurar mis Pagos")
                d_p = st.text_area("Datos de Pago", value=perf.get('datos_pago','') or "")
                if st.button("GUARDAR DATOS DE PAGO"):
                    supabase.table("perfiles_comercio").update({"datos_pago": d_p}).eq("id", perf['id']).execute()
                    st.success("Datos actualizados")

            with t4:
                st.subheader("Registrar Nuevo Socio")
                with st.form("form_reg", clear_on_submit=True):
                    rn = st.text_input("Nombre de Tienda")
                    rm = st.text_input("Email")
                    rt = st.text_input("WhatsApp")
                    ri = st.file_uploader("Cargar Portada", type=['jpg', 'png'])
                    # ÚNICO BOTÓN PERMITIDO DENTRO DEL FORM
                    submit = st.form_submit_button("REGISTRAR NUEVO SOCIO")
                    
                    if submit:
                        if rn and rm and rt and ri:
                            path_i = f"portadas/{random.randint(1000,9999)}.jpg"
                            supabase.storage.from_("fotos_productos").upload(path_i, ri.getvalue(), {"x-upsert": "true"})
                            url_i = supabase.storage.from_("fotos_productos").get_public_url(path_i)
                            supabase.table("perfiles_comercio").insert({"nombre_comercio":rn, "email_propietario":rm.lower(), "whatsapp":rt, "portada_url":url_i, "codigo_acceso": "LUXURY7"}).execute()
                            st.success(f"Socio {rn} registrado")

            if st.button("🚪 CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()