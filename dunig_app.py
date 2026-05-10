import streamlit as st
from supabase import create_client, Client
import urllib.parse
import uuid

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

PLANES_INFO = {
    "GRATUITO (Hasta 3 productos)": 3,
    "BRONCE (Hasta 10 productos)": 10,
    "PLATA (Hasta 25 productos)": 25,
    "ORO (Hasta 100 productos)": 100
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_data' not in st.session_state: st.session_state.user_data = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000000; color: #ffffff; }
    
    /* BOTÓN COMPRAR (PRINCIPAL) */
    .btn-comprar button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 55px !important; width: 100% !important; margin-top: 10px !important;
    }

    /* BOTÓN REGRESAR (SIN FONDO, DELGADO) */
    .btn-regresar button {
        background: transparent !important;
        color: #ffffff !important; 
        border: 1px solid rgba(255,255,255,0.3) !important;
        border-radius: 8px !important; 
        height: 30px !important; /* Más delgado */
        width: 100% !important; 
        font-size: 0.75rem !important;
        text-transform: uppercase; 
        letter-spacing: 2px;
        margin-top: 5px !important;
    }

    /* VIDEO FULL WIDTH */
    .video-full {
        width: 100vw; position: relative; left: 50%; right: 50%;
        margin-left: -50vw; margin-right: -50vw;
        background: #000; line-height: 0;
    }
    video { width: 100% !important; height: auto !important; max-height: 80vh; object-fit: cover; }

    /* INFO BAR */
    .info-luxury-box {
        display: flex; justify-content: space-between; align-items: center;
        background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
        padding: 0 15px; height: 50px; border-radius: 12px; 
        border: 1px solid rgba(212,175,55,0.4); margin-top: -10px;
    }
    .p-title { color: #D4AF37; font-weight: 700; text-transform: uppercase; font-size: 0.9rem; }
    .p-price { color: #39FF14; font-weight: 900; font-size: 1.1rem; }

    .img-cuadrada { width: 100%; aspect-ratio: 1/1; object-fit: cover; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================

es_admin = st.query_params.get("admin") == "true"
es_reg = st.query_params.get("reg") == "true"

# --- PANEL DE CONTROL (ADMIN) ---
if es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL SOCIO</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.container():
            m = st.text_input("Email Registrado")
            c = st.text_input("Código de Acceso", type="password")
            if st.button("ACCEDER AL PANEL"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m.lower()).execute()
                if res.data and str(res.data[0]['codigo_acceso']).upper() == c.upper():
                    st.session_state.logged_in = True
                    st.session_state.user_data = res.data[0]
                    st.rerun()
                else: st.error("Credenciales incorrectas")
    else:
        u = st.session_state.user_data
        st.success(f"Tienda: {u['nombre_comercio']} | Plan: {u['plan']}")
        if st.button("CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()
        
        with st.form("subir_pro", clear_on_submit=True):
            st.subheader("Publicar nuevo video")
            n_p = st.text_input("Nombre del Producto")
            p_p = st.number_input("Precio ($)", min_value=0.0)
            v_p = st.file_uploader("Video MP4", type=['mp4'])
            if st.form_submit_button("🚀 SUBIR PRODUCTO"):
                if n_p and v_p:
                    path = f"videos/{u['nombre_comercio']}/{uuid.uuid4()}.mp4"
                    supabase.storage.from_("fotos_productos").upload(path, v_p.getvalue())
                    url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                    supabase.table("productos").insert({
                        "nombre_producto": n_p, "precio": p_p, 
                        "video_url": url_v, "comercio_relacionado": u['nombre_comercio']
                    }).execute()
                    st.success("¡Producto en vivo!")

# --- REGISTRO ---
elif es_reg:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO SOCIO</h1>", unsafe_allow_html=True)
    with st.form("reg"):
        n = st.text_input("Nombre Tienda")
        e = st.text_input("Email")
        w = st.text_input("WhatsApp")
        plan = st.selectbox("Plan de Expansión", list(PLANES_INFO.keys()))
        img = st.file_uploader("Portada", type=['jpg', 'png'])
        if st.form_submit_button("REGISTRAR"):
            # Lógica de registro aquí...
            st.info("Solicitud recibida.")

# --- MALL ---
elif st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    cols = st.columns(2)
    for i, t in enumerate(tiendas):
        with cols[i % 2]:
            st.markdown(f'<img src="{t["portada_url"]}" class="img-cuadrada">', unsafe_allow_html=True)
            if st.button(f"ENTRAR {t['nombre_comercio'].upper()}", key=f"t_{t['id']}"):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        st.markdown('<div class="video-full">', unsafe_allow_html=True)
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="info-luxury-box"><span class="p-title">{p["nombre_producto"]}</span><span class="p-price">${p["precio"]}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="btn-comprar">', unsafe_allow_html=True)
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            # Lógica de WhatsApp
            msj = urllib.parse.quote(f"Hola {t['nombre_comercio']}, quiero {p['nombre_producto']}")
            st.link_button("IR AL WHATSAPP", f"https://wa.me/{t['whatsapp']}?text={msj}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="btn-regresar">', unsafe_allow_html=True)
        if st.button("REGRESAR AL MALL", key=f"back_{p['id']}"):
            ir_a('mall')
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()