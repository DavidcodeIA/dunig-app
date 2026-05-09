import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import time
from datetime import datetime, date

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

@st.cache_resource 
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

supabase = init_connection()

# --- LÓGICA DE NEGOCIO ---
def verificar_expiracion(perfil):
    if perfil.get('plan') == "GRATUITO":
        try:
            f_reg_raw = perfil.get('fecha_registro')
            fecha_reg = datetime.strptime(str(f_reg_raw), '%Y-%m-%d').date() if f_reg_raw else date.today()
            dias_transcurridos = (date.today() - fecha_reg).days
            if dias_transcurridos >= 7 and perfil.get('activo') == True:
                supabase.table("perfiles_comercio").update({"activo": False}).eq("id", perfil['id']).execute()
                return False
        except:
            return perfil.get('activo', False)
    return perfil.get('activo', False)

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS RESTAURADO Y MEJORADO)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    
    /* Burbuja de Precio Flotante */
    .price-bubble {
        position: absolute;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #D4AF37, #F9F295);
        color: black;
        padding: 8px 15px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 1.2rem;
        z-index: 100;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        border: 1px solid white;
    }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 30px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 50px;
    }

    .video-container {
        position: relative;
        width: 100%;
        border-radius: 25px;
        overflow: hidden;
        border: 2px solid #D4AF37;
        margin-bottom: 10px;
    }
    
    .img-mall-luxury {
        width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 25px;
        border: 2px solid #D4AF37;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VISTAS
# ==========================================
es_admin_master = st.query_params.get("admin") == "true"

# --- VISTA: MALL ---
if not es_admin_master and st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    datos = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
    tiendas = [t for t in datos if verificar_expiracion(t)]
    
    if not tiendas: st.info("Próximamente...")
    else:
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    url = t.get("portada_url", "")
                    with cols[j]:
                        if url.lower().endswith(('.mp4', '.mov')):
                            st.markdown(f'<video autoplay loop muted playsinline class="img-mall-luxury"><source src="{url}"></video>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<img src="{url}" class="img-mall-luxury">', unsafe_allow_html=True)
                        
                        if st.button(f"VER {t['nombre_comercio'].upper()}", key=f"mall_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

# --- VISTA: TIENDA (VITRINA CORRECCIÓN TOTAL) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("⬅️"): ir_a('mall')
    with col_title:
        st.markdown(f"<h2 style='color:#D4AF37; margin:0;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)

    # Traer productos
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        with st.container():
            # Contenedor de Video con Burbuja de Precio
            v_url = p.get('video_url', '')
            st.markdown(f"""
                <div class="video-container">
                    <div class="price-bubble">${p['precio']}</div>
                    <video width="100%" controls autoplay loop muted playsinline>
                        <source src="{v_url}" type="video/mp4">
                    </video>
                </div>
            """, unsafe_allow_html=True)
            
            # Botón de Compra Funcional
            msg = urllib.parse.quote(f"Hola {t['nombre_comercio']}, me interesa el producto: {p['nombre_producto']} de D'UNIG LUXURY")
            whatsapp_url = f"https://wa.me/{t['whatsapp']}?text={msg}"
            
            st.link_button(f"🛒 COMPRAR {p['nombre_producto']}", whatsapp_url, use_container_width=True)
            st.write("---")

# --- VISTA: PANEL (ADMIN) ---
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE SOCIO</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.form("login"):
            l_email = st.text_input("Email").strip().lower()
            l_code = st.text_input("Código", type="password").upper()
            if st.form_submit_button("INGRESAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", l_email).execute()
                if res.data and str(res.data[0].get('codigo_acceso')).upper() == l_code:
                    st.session_state.logged_in, st.session_state.user_email = True, l_email
                    st.rerun()
                else: st.error("Acceso Denegado")
    else:
        st.success(f"Sesión: {st.session_state.user_email}")
        if st.button("CERRAR SESIÓN"):
            st.session_state.logged_in = False
            st.rerun()