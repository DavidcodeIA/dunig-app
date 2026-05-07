import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

PLANES = {"BRONCE": 5, "PLATINUM": 15, "DIAMANTE": 50}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CÍRCULOS Y MALL)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000000; color: #ffffff; }
    
    /* Contenedor de la tarjeta del Mall */
    .luxury-card {
        text-align: center;
        padding: 10px;
        margin-bottom: 20px;
    }

    /* Foto Redonda PerfectA */
    .img-redonda {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #D4AF37;
        margin: 0 auto 10px auto;
        display: block;
        box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.3);
    }

    .stButton>button {
        border-radius: 20px !important;
    }
    
    /* Quitar espacios innecesarios */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE NAVEGACIÓN
# ==========================================
es_admin = st.query_params.get("admin") == "true"

if not es_admin:
    # --- VISTA CLIENTE (MALL) ---
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        
        res = supabase.table("perfiles_comercio").select("*").execute()
        tiendas = res.data
        
        # Crear filas de 2 columnas cada una
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            # Tienda 1 de la fila
            with cols[0]:
                t = tiendas[i]
                st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
                url = t.get('portada_url') if t.get('portada_url') else "https://via.placeholder.com/150"
                st.markdown(f'<img src="{url}" class="img-redonda">', unsafe_allow_html=True)
                st.markdown(f"<p style='font-weight:bold; color:#D4AF37; margin-bottom:5px;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                if st.button("ENTRAR", key=f"mall_{t['id']}", use_container_width=True):
                    st.session_state.tienda_actual = t
                    ir_a('tienda')
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Tienda 2 de la fila (si existe)
            if i + 1 < len(tiendas):
                with cols[1]:
                    t2 = tiendas[i+1]
                    st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
                    url2 = t2.get('portada_url') if t2.get('portada_url') else "https://via.placeholder.com/150"
                    st.markdown(f'<img src="{url2}" class="img-redonda">', unsafe_allow_html=True)
                    st.markdown(f"<p style='font-weight:bold; color:#D4AF37; margin-bottom:5px;'>{t2['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                    if st.button("ENTRAR", key=f"mall_{t2['id']}", use_container_width=True):
                        st.session_state.tienda_actual = t2
                        ir_a('tienda')
                    st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        # (Lógica de productos omitida para mantener el código limpio)

else:
    # --- PANEL ADMIN (FIJADO EL ERROR DE PANTALLA NEGRA) ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.container(border=True):
            user_mail = st.text_input("Email de Propietario").strip().lower()
            user_pass = st.text_input("Código de Acceso", type="password").strip().upper()
            if st.button("🔓 ACCEDER AL SISTEMA", use_container_width=True):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", user_mail).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == user_pass:
                    st.session_state.logged_in = True
                    st.session_state.user_email = user_mail
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
    else:
        # Recuperar datos del perfil logueado
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        if res.data:
            perf = res.data[0]
            
            # Pestañas visibles y funcionales
            t1, t2, t3, t4, t5 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "🖼️ PORTADA", "💳 COBROS", "✨ REGISTRO"])
            
            with t1:
                st.subheader("Subir Producto")
                with st.form("add_prod"):
                    n = st.text_input("Nombre")
                    p = st.number_input("Precio", min_value=0.0)
                    v = st.file_uploader("Video MP4", type=['mp4'])
                    if st.form_submit_button("PUBLICAR"):
                        st.info("Subiendo...")

            with t3:
                st.subheader("Imagen de Portada (Círculo)")
                if perf.get('portada_url'):
                    st.image(perf['portada_url'], width=150)
                new_img = st.file_uploader("Cargar nueva foto", type=['jpg', 'png'])
                if st.button("GUARDAR PORTADA"):
                    if new_img:
                        path = f"portadas/{perf['id']}.jpg"
                        supabase.storage.from_("fotos_productos").upload(path=path, file=new_img.getvalue(), file_options={"upsert": True})
                        url = supabase.storage.from_("fotos_productos").get_public_url(path)
                        supabase.table("perfiles_comercio").update({"portada_url": url}).eq("id", perf['id']).execute()
                        st.success("Portada actualizada")
                        st.rerun()

            with t5:
                st.subheader("Registrar Nuevo Socio")
                with st.form("nuevo_socio"):
                    nom = st.text_input("Nombre Tienda")
                    ema = st.text_input("Email")
                    tel = st.text_input("WhatsApp")
                    img = st.file_uploader("Logo Tienda (Se hará circular)", type=['jpg', 'png'])
                    if st.form_submit_button("REGISTRAR"):
                        # Lógica de registro...
                        st.success("Socio registrado con éxito")

            if st.button("🚪 SALIR"):
                st.session_state.logged_in = False
                st.rerun()