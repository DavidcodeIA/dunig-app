import streamlit as st
from supabase import create_client, Client
import random

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN LUXURY
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", initial_sidebar_state="collapsed")

# Conexión Segura a Supabase
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("⚠️ Error de conexión: Revisa tus Secrets en Streamlit Cloud.")
    st.stop()

# --- FUNCIÓN DE NAVEGACIÓN ---
def navegar(destino, com=None):
    st.session_state.pagina = destino
    if com:
        st.session_state.comercio_sel = com
    st.rerun()

# --- FUNCIÓN PARA BORRAR PRODUCTO ---
def borrar_producto(id_prod):
    try:
        supabase.table("productos").delete().eq("id", id_prod).execute()
        st.toast("✅ Producto eliminado del inventario")
        st.rerun()
    except Exception as e:
        st.error(f"Error al eliminar: {e}")

# Inicialización de estados
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None

# ==========================================
# 2. ESTILOS LUXURY 3D (CSS)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Poppins:wght@300;400;600&display=swap');
    
    .main { background: radial-gradient(circle, #1a1c23 0%, #0e1117 100%); }
    
    .title-luxury {
        font-family: 'Playfair Display', serif;
        color: #D4AF37;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        font-size: 3rem;
    }

    .stButton>button {
        background: linear-gradient(145deg, #d4af37, #b8860b);
        color: white !important;
        border: none;
        padding: 12px 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 0px #8b6d05, 0px 8px 12px rgba(0,0,0,0.4);
        transition: all 0.2s ease;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        width: 100%;
        text-transform: uppercase;
    }
    
    .stButton>button:hover { transform: translateY(2px); box-shadow: 0px 2px 0px #8b6d05; }
    
    /* Botón de Borrar (Rojo Luxury) */
    div[data-testid="stVerticalBlock"] > div:nth-child(2) .stButton>button {
        background: linear-gradient(145deg, #ff4b4b, #b91d1d) !important;
        box-shadow: 0px 4px 0px #7b1313, 0px 8px 12px rgba(0,0,0,0.4) !important;
    }

    .card-luxury {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(212, 175, 55, 0.2);
        margin-bottom: 15px;
    }
    
    .price-tag { color: #D4AF37; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE PÁGINAS
# ==========================================

# --- PÁGINA: INICIO ---
if st.session_state.pagina == "inicio":
    st.markdown("<h1 class='title-luxury'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns(2)
    with col1: st.button("🛒 CLIENTE", on_click=navegar, args=("centro_comercial",))
    with col2: st.button("🏢 PROPIETARIO", on_click=navegar, args=("login_comercio",))

# --- PÁGINA: LOGIN ---
elif st.session_state.pagina == "login_comercio":
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>🔑 ACCESO AL PANEL</h2>", unsafe_allow_html=True)
    nom_login = st.text_input("Nombre de tu Negocio")
    if st.button("INGRESAR"):
        if nom_login:
            st.session_state.comercio_sesion = nom_login.strip()
            navegar("panel_carga")
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- PÁGINA: PANEL DE GESTIÓN (MEJORADO) ---
elif st.session_state.pagina == "panel_carga":
    nombre_c = st.session_state.comercio_sesion
    st.markdown(f"<h2 style='color:#D4AF37;'>⚙️ PANEL: {nombre_c}</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🚀 Cargar Nuevo", "📦 Inventario", "🖼️ Perfil"])
    
    with tab1:
        with st.form("form_carga", clear_on_submit=True):
            p_nom = st.text_input("Nombre del Producto")
            p_pre = st.number_input("Precio ($)", min_value=0.0)
            p_vid = st.file_uploader("Video (MP4)", type=['mp4'])
            if st.form_submit_button("🚀 PUBLICAR AHORA"):
                if p_nom and p_vid:
                    try:
                        n_limpio = "".join(e for e in p_nom if e.isalnum())
                        path = f"productos/{n_limpio}_{random.randint(1000,9999)}.mp4"
                        supabase.storage.from_("fotos_productos").upload(path, p_vid.getvalue())
                        url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                        supabase.table("productos").insert({"nombre_producto": p_nom, "precio": p_pre, "video_url": url_v, "comercio_propietario": nombre_c}).execute()
                        st.success("✅ ¡Publicado!")
                        st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    with tab2:
        st.subheader("Tu Stock Actual")
        prods = supabase.table("productos").select("*").eq("comercio_propietario", nombre_c).execute()
        if prods.data:
            for p in prods.data:
                with st.container():
                    col_info, col_del = st.columns([3, 1])
                    with col_info:
                        st.markdown(f"**{p['nombre_producto']}** - {p['precio']}$")
                    with col_del:
                        if st.button("🗑️ Borrar", key=f"del_{p['id']}"):
                            borrar_producto(p['id'])
                    st.write("---")
        else: st.info("No tienes productos en stock.")

    with tab3:
        st.write("Configura tu logo y datos de contacto aquí.")
        # (Aquí iría el código de perfil que ya tenemos)

    st.button("🔙 SALIR", on_click=navegar, args=("inicio",))

# --- PÁGINA: CENTRO COMERCIAL ---
elif st.session_state.pagina == "centro_comercial":
    st.markdown("<h1 class='title-luxury'>🛒 CENTRO COMERCIAL</h1>", unsafe_allow_html=True)
    try:
        # Se asume que los nombres de comercios están en la tabla 'perfiles_comercio' o 'productos'
        res = supabase.table("productos").select("comercio_propietario").execute()
        comercios_unicos = list(set([item['comercio_propietario'] for item in res.data]))
        
        for c in comercios_unicos:
            st.markdown(f"<div class='card-luxury'><h3>💎 {c}</h3></div>", unsafe_allow_html=True)
            st.button(f"VISITAR {c}", key=f"v_{c}", on_click=navegar, args=("vitrina_personal", c))
    except: st.info("Buscando comercios...")
    st.button("🔙 INICIO", on_click=navegar, args=("inicio",))

# --- PÁGINA: VITRINA PERSONAL ---
elif st.session_state.pagina == "vitrina_personal":
    tienda = st.session_state.comercio_sel
    st.markdown(f"<h1 class='title-luxury'>{tienda}</h1>", unsafe_allow_html=True)
    prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
    if prods.data:
        for p in prods.data:
            st.video(p['video_url'])
            st.subheader(p['nombre_producto'])
            st.markdown(f"<p class='price-tag'>{p['precio']}$</p>", unsafe_allow_html=True)
            st.write("---")
    st.button("🔙 VOLVER", on_click=navegar, args=("centro_comercial",))
