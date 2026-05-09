import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# Estados de la App
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS PROFESIONAL (UI INYECTADA EN VIDEO)
# ==========================================
st.markdown("""
    <style>
    /* Eliminar basura de Streamlit */
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .stApp { background-color: #000; }
    header, footer { visibility: hidden; }
    
    /* Contenedor Maestro de Video */
    .video-container {
        position: relative;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
        background: #000;
        border-bottom: 2px solid #333;
    }

    /* Video de Fondo */
    iframe, video {
        width: 100vw !important;
        height: 100vh !important;
        object-fit: cover !important;
    }

    /* CAPA DE INTERFAZ (UI) */
    .ui-layer {
        position: absolute;
        bottom: 50px;
        left: 25px;
        z-index: 999;
        pointer-events: none;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    /* Iconos Estilo Botón */
    .icon-click { pointer-events: auto !important; cursor: pointer; }
    
    /* Estilo de los textos (Azul con borde blanco como tu ejemplo) */
    .text-luxury {
        color: #1E4D92;
        font-weight: 900;
        text-transform: uppercase;
        -webkit-text-stroke: 1.5px white;
        margin: 0;
        line-height: 1;
    }
    .brand-title { font-size: 2.5rem; }
    .product-title { font-size: 2.8rem; }

    /* Burbuja de Precio */
    .price-tag {
        background: #FFD700;
        color: #000;
        padding: 5px 20px;
        border-radius: 50px;
        font-size: 2rem;
        font-weight: 900;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }

    /* Botones invisibles de Streamlit para iconos */
    .stButton > button {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        font-size: 60px !important;
        color: white !important;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.8);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"

# --- MODO ADMIN (EL PANEL QUE FALTA) ---
if es_admin:
    if not st.session_state.logged_in:
        st.markdown("<h2 style='text-align:center; color:white;'>ACCESO PANEL CONTROL</h2>", unsafe_allow_html=True)
        with st.container(border=True):
            email = st.text_input("Email").lower()
            code = st.text_input("Código", type="password")
            if st.button("ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email).execute()
                if res.data and str(res.data[0]['codigo_acceso']) == code:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.rerun()
    else:
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        st.title(f"Panel: {perf['nombre_comercio']}")
        
        t1, t2 = st.tabs(["🎥 GESTIONAR VITRINA", "⚙️ MI PERFIL"])
        
        with t1:
            # Subir Producto
            with st.expander("➕ SUBIR NUEVO VIDEO"):
                with st.form("upload"):
                    nom = st.text_input("Nombre del Producto")
                    pre = st.number_input("Precio ($)")
                    vid = st.file_uploader("Video Vertical", type=['mp4'])
                    if st.form_submit_button("PUBLICAR"):
                        path = f"v/{random.randint(100,999)}_{perf['id']}.mp4"
                        supabase.storage.from_("fotos_productos").upload(path, vid.getvalue())
                        url = supabase.storage.from_("fotos_productos").get_public_url(path)
                        supabase.table("productos").insert({"nombre_producto":nom, "precio":pre, "video_url":url, "comercio_relacionado":perf['nombre_comercio']}).execute()
                        st.success("¡En línea!"); st.rerun()
            
            # Lista de Productos
            prods = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            for p in prods:
                c1, c2 = st.columns([4,1])
                c1.write(f"📦 {p['nombre_producto']} - ${p['precio']}")
                if c2.button("🗑️", key=p['id']):
                    supabase.table("productos").delete().eq("id", p['id']).execute()
                    st.rerun()

# --- MODO USUARIO (MALL Y TIENDA) ---
else:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG MALL</h1>", unsafe_allow_html=True)
        tiendas = supabase.table("perfiles_comercio").select("*").execute().data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.image(t['portada_url'])
                        if st.button(f"ENTRAR A {t['nombre_comercio'].upper()}", key=t['id']):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        
        for p in prods:
            # EL CONTENEDOR TIKTOK
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            
            # Video de Fondo
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)

            # Capa de Iconos (UI)
            st.markdown('<div class="ui-layer">', unsafe_allow_html=True)
            
            # 1. Flecha Volver
            if st.button("↩️", key=f"v_{p['id']}"): ir_a('mall')
            
            # 2. Precio
            st.markdown(f'<div class="price-tag">{p["precio"]}$</div>', unsafe_allow_html=True)
            
            # 3. Punto de Venta (Pagar)
            if st.button("💳", key=f"p_{p['id']}"):
                st.toast(f"Paga a {t['nombre_comercio']} vía WhatsApp")
            
            # 4. Textos de Identificación
            st.markdown(f'<p class="text-luxury brand-title">{t["nombre_comercio"]}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="text-luxury product-title">{p["nombre_producto"]}</p>', unsafe_allow_html=True)
            
            st.markdown('</div></div>', unsafe_allow_html=True)