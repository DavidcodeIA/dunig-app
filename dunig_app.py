import streamlit as st
from supabase import create_client

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Estados de navegación
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

@st.cache_resource 
def init_connection():
    try:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except: return None

supabase = init_connection()

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS INTEGRAL (MALL + VIDEOS + PANELES)
# ==========================================
st.markdown("""
    <style>
    header, footer, [data-testid="stSidebar"] { visibility: hidden; display: none !important; }
    
    html, body, .main, [data-testid="stAppViewBlockContainer"] {
        overflow: hidden !important;
        margin: 0 !important; padding: 0 !important;
        width: 100vw !important; height: 100vh !important;
        background-color: #000 !important;
    }

    [data-testid="stAppViewBlockContainer"] { margin-top: -100px !important; }

    /* Estilo para los Paneles de Registro/Control */
    .admin-panel {
        background: #111;
        height: 100vh;
        padding: 40px 20px;
        color: white;
        overflow-y: auto !important;
    }

    /* Botones y Inputs para Registro de Socio */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #222 !important;
        color: gold !important;
        border: 1px solid #D4AF37 !important;
    }

    /* BOTONES FLOTANTES */
    div.stButton > button[key="btn_admin"] {
        position: fixed; top: 20px; right: 20px; z-index: 3000;
        background: rgba(212, 175, 55, 0.2) !important;
        border: 1px solid #D4AF37 !important; color: #D4AF37 !important;
        border-radius: 10px; font-size: 0.7rem;
    }
    
    div.stButton > button[key^="back_"] {
        position: fixed; top: 30px; left: 20px; z-index: 2000;
        background: rgba(0,0,0,0.7) !important; color: #FF5F1F !important;
        border: 2px solid #FF5F1F !important; border-radius: 50px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VISTAS DE LA APP
# ==========================================

# --- BOTÓN DE ADMINISTRACIÓN (Solo visible en el Mall) ---
if st.session_state.view == 'mall':
    if st.button("⚙️ PANEL", key="btn_admin"):
        ir_a('admin_panel')

# --- VISTA: MALL (Pantalla Dividida) ---
if st.session_state.view == 'mall':
    if supabase:
        tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).limit(2).execute().data
        for idx, t in enumerate(tiendas):
            st.markdown(f'<div class="shop-half"><img src="{t.get("portada_url", "")}"><div class="shop-label">{t["nombre_comercio"]}</div></div>', unsafe_allow_html=True)
            if st.button(f"Entrar {idx}", key=f"link_{t['id']}"):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA: TIENDA (Videos Inmersivos) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if supabase and t:
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        if st.button("⬅ VOLVER", key="back_mall"): ir_a('mall')
        for idx, p in enumerate(prods):
            st.markdown(f"""
                <div class="snap-section">
                    <video class="tiktok-video" loop playsinline muted preload="auto"><source src="{p['video_url']}"></video>
                    <div style="position:absolute; bottom:120px; left:25px; z-index:500;">
                        <h1 style="color:#D4AF37; margin:0;">@{t['nombre_comercio']}</h1>
                        <h2 style="color:#39FF14;">$ {p['precio']}</h2>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# --- VISTA: PANEL DE CONTROL Y REGISTRO (Nueva) ---
elif st.session_state.view == 'admin_panel':
    st.markdown('<div class="admin-panel">', unsafe_allow_html=True)
    if st.button("⬅ SALIR DEL PANEL", key="back_admin"): ir_a('mall')
    
    st.title("⚜️ Panel de Control D'UNIG")
    
    tab1, tab2 = st.tabs(["📊 Gestión de Comercios", "📝 Registro de Nuevo Socio"])
    
    with tab1:
        st.subheader("Comercios Activos")
        if supabase:
            lista = supabase.table("perfiles_comercio").select("nombre_comercio, activo").execute().data
            st.table(lista)
            
    with tab2:
        st.subheader("REGISTRO DE NUEVO SOCIO")
        with st.form("registro_socio"):
            nombre = st.text_input("Nombre del Comercio")
            propietario = st.text_input("Nombre del Propietario")
            categoria = st.selectbox("Categoría", ["Moda", "Lujo", "Tecnología", "Joyas"])
            portada = st.text_input("URL de Imagen de Portada (Mall)")
            
            if st.form_submit_button("REGISTRAR COMERCIO"):
                # Aquí iría tu lógica de supabase.table("perfiles_comercio").insert(...)
                st.success(f"¡{nombre} ha sido registrado con éxito!")
    
    st.markdown('</div>', unsafe_allow_html=True)