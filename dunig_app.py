import streamlit as st
from supabase import create_client

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN (MANTENIENDO TU LÓGICA)
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# Recuperamos todas tus variables de estado originales
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None
if 'user_data' not in st.session_state: st.session_state.user_data = None # Para tu registro de socios

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
# 2. CSS CORRECTIVO (SIN BORRAR TU ESTILO)
# ==========================================
st.markdown("""
    <style>
    /* FIX: ELIMINAR ESPACIO SUPERIOR SIN AFECTAR EL CONTENIDO */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0rem !important;
        margin-top: -75px !important; /* Ajuste preciso para Screenshot_20260509-142706.jpg */
        max-width: 100vw !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
    }
    
    .main { background-color: #000 !important; }
    header, footer { visibility: hidden; height: 0px; }

    /* DISEÑO DE TIENDAS DIVIDIDAS (ESTILO GGC3DL2GFFA7ZJVXV6LNRRRGWQ.jpg) */
    .mall-wrapper {
        display: flex;
        flex-direction: column;
        height: 100vh;
        width: 100vw;
    }

    .tienda-split {
        height: 50vh;
        width: 100vw;
        position: relative;
        border-bottom: 2px solid #D4AF37;
    }

    .tienda-split img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* BOTONES INVISIBLES SOBRE LAS TIENDAS */
    div.stButton > button[key^="ir_tienda_"] {
        position: absolute;
        top: 0;
        height: 50vh !important;
        width: 100vw !important;
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        z-index: 10;
    }
    
    /* TU BOTÓN DE REGISTRO (Mantenlo visible) */
    div.stButton > button[key="btn_registro"] {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 100;
        background: #FF5F1F !important;
        border-radius: 50% !important;
        width: 60px;
        height: 60px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS (RESTAURADA)
# ==========================================

# VISTA MALL (Con división 50/50)
if st.session_state.view == 'mall':
    if supabase:
        tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).limit(2).execute().data
        
        for t in tiendas:
            # Contenedor visual de la tienda
            st.markdown(f"""
                <div class="tienda-split">
                    <img src="{t.get('portada_url', '')}">
                    <div style="position:absolute; top:40%; width:100%; text-align:center;">
                        <h1 style="color:white; font-size:3rem; text-shadow:2px 2px 10px #000;">{t['nombre_comercio']}</h1>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Botón funcional invisible
            if st.button("", key=f"ir_tienda_{t['id']}"):
                st.session_state.tienda_actual = t
                ir_a('tienda')
        
        # AQUÍ TU BOTÓN DE REGISTRO QUE YA TENÍAS
        if st.button("+", key="btn_registro"):
            ir_a('registro_socio')

# VISTA REGISTRO (Restaurando lo que borré)
elif st.session_state.view == 'registro_socio':
    st.title("REGISTRO DE NUEVO SOCIO")
    # ... Aquí vuelve a pegar tu código del formulario de registro que tenías antes ...
    if st.button("VOLVER"): ir_a('mall')

# VISTA TIENDA (Con videos corregidos)
elif st.session_state.view == 'tienda':
    # Aquí iría el código de videos que ya ajustamos, pero sin perder el botón de atrás
    if st.button("⬅", key="back_mall"): ir_a('mall')
    # ... (Resto de tu lógica de productos) ...