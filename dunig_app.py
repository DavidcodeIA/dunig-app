import streamlit as st
from supabase import create_client, Client
import urllib.parse
import uuid

# ==========================================
# 1. CONEXIÓN (Asegúrate de tener tus Secrets)
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# Estados de sesión
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS PROFESIONAL (Full Width + Nav Bar)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000; color: #fff; }
    .video-full { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; background: #000; line-height: 0; }
    video { width: 100% !important; height: auto !important; max-height: 80vh; object-fit: cover; }

    /* FILA DE CONTROL: Flecha + Info */
    div[data-testid="stHorizontalBlock"] .stButton button { 
        background: transparent !important; border: 2px solid #fff !important; 
        color: #fff !important; border-radius: 12px !important; width: 50px !important; height: 50px !important;
    }
    
    .product-details {
        display: flex; justify-content: space-between; align-items: center;
        background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
        padding: 0 15px; height: 50px; border-radius: 12px; border: 1px solid rgba(212,175,55,0.4);
    }
    .txt-name { color: #D4AF37; font-weight: 700; text-transform: uppercase; font-size: 0.9rem; }
    .txt-price { color: #39FF14; font-weight: 900; font-size: 1.1rem; }

    /* BOTÓN COMPRAR */
    .btn-buy button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        color: #000 !important; font-weight: 800 !important; border-radius: 15px !important; height: 55px !important;
    }
    .img-mall { width: 100%; aspect-ratio: 1/1; object-fit: cover; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================

# --- MODO ADMIN (Para que el socio suba productos) ---
if st.query_params.get("admin") == "true":
    st.title("💎 PANEL DE SOCIO LUXURY")
    if not st.session_state.logged_in:
        email = st.text_input("Tu Email")
        pin = st.text_input("PIN", type="password")
        if st.button("ENTRAR AL PANEL"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email.lower()).execute()
            if res.data and str(res.data[0]['codigo_acceso']) == pin:
                st.session_state.logged_in = True
                st.session_state.user_data = res.data[0]
                st.rerun()
    else:
        user = st.session_state.user_data
        st.subheader(f"Gestionando: {user['nombre_comercio']}")
        
        with st.form("subir_producto", clear_on_submit=True):
            nombre = st.text_input("Nombre del Producto")
            precio = st.number_input("Precio ($)", min_value=0.0)
            archivo = st.file_uploader("Video del Producto (MP4)", type=['mp4'])
            
            if st.form_submit_button("🚀 PUBLICAR EN EL MALL"):
                if archivo and nombre:
                    file_path = f"videos/{user['nombre_comercio']}/{uuid.uuid4()}.mp4"
                    # Subir a Supabase Storage
                    supabase.storage.from_("fotos_productos").upload(file_path, archivo.getvalue())
                    url_video = supabase.storage.from_("fotos_productos").get_public_url(file_path)
                    # Guardar en Tabla
                    supabase.table("productos").insert({
                        "nombre_producto": nombre,
                        "precio": precio,
                        "video_url": url_video,
                        "comercio_relacionado": user['nombre_comercio']
                    }).execute()
                    st.success("¡Producto publicado con éxito!")

# --- VISTA: MALL ---
elif st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    cols = st.columns(2)
    for idx, t in enumerate(tiendas):
        with cols[idx % 2]:
            st.markdown(f'<img src="{t["portada_url"]}" class="img-mall">', unsafe_allow_html=True)
            if st.button(f"ENTRAR {t['nombre_comercio'].upper()}", key=f"t_{t['id']}", use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA: TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        st.markdown('<div class="video-full">', unsafe_allow_html=True)
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns([1, 5])
        with c1:
            if st.button("←", key=f"back_{p['id']}"): ir_a('mall')
        with c2:
            st.markdown(f'<div class="product-details"><span class="txt-name">{p["nombre_producto"]}</span><span class="txt-price">${p["precio"]}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="btn-buy">', unsafe_allow_html=True)
        if st.button("🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            msj = f"Hola {t['nombre_comercio']}, quiero comprar {p['nombre_producto']}."
            st.link_button("CONFIRMAR WHATSAPP", f"https://wa.me/{t['whatsapp']}?text={urllib.parse.quote(msj)}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()