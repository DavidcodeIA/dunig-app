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

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS PARA CUADRÍCULA MÓVIL (2 COLUMNAS)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    
    /* Contenedor de la Cuadrícula */
    .mall-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr); /* FUERZA 2 COLUMNAS EN MÓVIL */
        gap: 10px;
        padding: 10px;
    }

    /* Cada tarjeta de tienda */
    .tienda-card {
        text-align: center;
        background: rgba(255,255,255,0.02);
        border-radius: 15px;
        padding-bottom: 5px;
    }

    /* Imagen Rectangular Ovalada Pequeña */
    .img-mall {
        width: 100%;
        aspect-ratio: 3 / 4; /* Proporción vertical como la imagen 1778270290959394695076444703398.jpg */
        object-fit: cover;
        border-radius: 15px; /* Esquinas ovaladas */
        border: 1px solid #D4AF37;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }

    .tienda-nombre {
        color: #D4AF37;
        font-size: 0.7rem;
        font-weight: bold;
        margin-top: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Botón Invisible sobre la imagen para que sea clickeable */
    .stButton button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #8A6E2F) !important;
        color: black !important;
        font-size: 10px !important;
        height: 25px !important;
        border-radius: 20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VISTA DEL MALL (CUADRÍCULA)
# ==========================================
if st.session_state.view == 'mall':
    st.markdown("<h3 style='text-align:center; color:#D4AF37;'>D'UNIG LUXURY MALL</h3>", unsafe_allow_html=True)
    
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    
    # Creamos el contenedor de la cuadrícula
    grid_html = '<div class="mall-grid">'
    
    # Generamos el contenido de cada tienda
    # Nota: Usamos columnas de Streamlit solo para los botones, el resto es HTML puro para control total
    cols = st.columns(2) 
    
    for idx, t in enumerate(tiendas):
        col_idx = idx % 2
        with cols[col_idx]:
            # Imagen y Nombre
            st.markdown(f"""
                <div class="tienda-card">
                    <img src="{t.get('portada_url')}" class="img-mall">
                    <div class="tienda-nombre">{t['nombre_comercio']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Botón de entrada
            if st.button("ENTRAR", key=f"btn_{t['id']}", use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# ==========================================
# 4. VISTA DE LA TIENDA
# ==========================================
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
    
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    if not prods:
        st.info("Esta tienda aún no tiene productos.")
    
    for p in prods:
        with st.container(border=True):
            st.markdown(f"<h4 style='color:#D4AF37;'>{p['nombre_producto']}</h4>", unsafe_allow_html=True)
            st.video(p['video_url'])
            st.markdown(f"<h3 style='color:#39FF14;'>${p['precio']}</h3>", unsafe_allow_html=True)
            if st.button(f"🛒 PEDIR AHORA", key=f"buy_{p['id']}", use_container_width=True):
                # Aquí iría la lógica del WhatsApp
                msj = f"Hola {t['nombre_comercio']}, me interesa {p['nombre_producto']}."
                st.link_button("WHATSAPP VENDEDOR", f"https://wa.me/{t['whatsapp']}?text={msj}")