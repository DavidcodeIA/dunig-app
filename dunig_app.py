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

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY + NAVEGACIÓN INTEGRADA
# ==========================================
st.markdown("""
    <style>
    .main { background: #000; color: #fff; }
    
    /* Portadas del Mall Cuadradas */
    .img-cuadrada { 
        width: 100%; aspect-ratio: 1/1; object-fit: cover; 
        border-radius: 5px; margin-bottom: 10px; 
    }
    
    /* Contenedor de Video TikTok */
    .video-wrapper { 
        position: relative; width: 100%; max-width: 400px; 
        margin: auto; border-radius: 20px; overflow: hidden; 
        border: 1px solid #222;
    }
    
    /* Capa de info dentro del video (Safe Zone) */
    .video-overlay-tienda {
        position: absolute; top: 15%; left: 5%;
        color: rgba(255,255,255,0.7); font-size: 0.9rem;
        text-shadow: 1px 1px 2px #000;
    }

    /* FILA DE ACCIÓN (Flecha + Info) */
    .action-row {
        display: flex; align-items: center; gap: 10px;
        width: 100%; max-width: 400px; margin: 15px auto 5px auto;
    }

    .info-container {
        flex-grow: 1; display: flex; justify-content: space-between;
        align-items: center; background: rgba(255,255,255,0.05);
        padding: 10px 15px; border-radius: 12px; border: 1px solid #333;
    }

    .p-name { color: #D4AF37; font-weight: 700; text-transform: uppercase; font-size: 1rem; }
    .p-price { color: #39FF14; font-weight: 900; font-size: 1.1rem; }

    /* Botones */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #8A6E2F) !important;
        color: #000 !important; font-weight: 800; border-radius: 12px !important;
        border: none !important; height: 45px;
    }

    /* Botón Flecha Blanca */
    .back-btn>button {
        background: transparent !important; color: #fff !important;
        border: 1px solid #fff !important; width: 45px !important;
        font-size: 1.2rem !important;
    }
    
    video { width: 100% !important; height: auto !important; object-fit: cover !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VISTAS
# ==========================================

# --- VISTA: MALL ---
if st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(tiendas):
                t = tiendas[i+j]
                with cols[j]:
                    st.markdown(f'<img src="{t["portada_url"]}" class="img-cuadrada">', unsafe_allow_html=True)
                    if st.button(f"ENTRAR", key=f"t_{t['id']}", use_container_width=True):
                        st.session_state.tienda_actual = t
                        ir_a('tienda')

# --- VISTA: TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        # 1. Video con nombre de tienda arriba
        st.markdown(f'''
            <div class="video-wrapper">
                <div class="video-overlay-tienda">@{t['nombre_comercio'].lower()}</div>
        ''', unsafe_allow_html=True)
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 2. FILA DE ACCIÓN (Flecha Regresar + Nombre + Precio)
        col_back, col_info = st.columns([1, 5])
        
        with col_back:
            st.markdown('<div class="back-btn">', unsafe_allow_html=True)
            if st.button("←", key=f"back_{p['id']}"):
                ir_a('mall')
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_info:
            st.markdown(f'''
                <div class="info-container">
                    <span class="p-name">{p['nombre_producto']}</span>
                    <span class="p-price">${p['precio']}</span>
                </div>
            ''', unsafe_allow_html=True)
        
        # 3. Botón Comprar
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            msj = f"¡Hola! Estoy interesado en {p['nombre_producto']} de su tienda en D'UNIG LUXURY."
            st.link_button("IR AL WHATSAPP", f"https://wa.me/{t['whatsapp']}?text={urllib.parse.quote(msj)}")
        
        st.divider()

# ==========================================
# 4. PANEL ADMIN (RESUMIDO)
# ==========================================
elif st.query_params.get("admin") == "true":
    st.title("⚙️ PANEL SOCIO")
    # ... (Aquí va tu lógica de login y subida de productos)