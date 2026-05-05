import streamlit as st
from supabase import create_client, Client
import random

# 1. Configuración de Alta Velocidad
st.set_page_config(page_title="D'UNIG PLATINUM", layout="centered")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# 2. Caché para Imágenes de Fondo (Evita que se cuelgue al recargar)
@st.cache_data
def get_banner(url_img):
    return url_img

# --- NAVEGACIÓN RÁPIDA ---
if 'view' not in st.session_state: st.session_state.view = 'mall'

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# 3. ESTILOS CSS OPTIMIZADOS
st.markdown("""
    <style>
    .main { background-color: #000000; }
    .stButton>button {
        background: linear-gradient(90deg, #D4AF37, #8B6B1E) !important;
        color: white !important;
        border-radius: 12px !important;
        width: 100%;
        height: 50px;
        font-weight: bold !important;
        border: none !important;
    }
    .video-container {
        border: 1px solid #D4AF37;
        border-radius: 15px;
        overflow: hidden;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- VISTA 1: MALL (CENTRO COMERCIAL VISUAL) ---
if st.session_state.view == 'mall':
    # Banner Propietario (Carga rápida desde caché)
    img_admin = get_banner("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/banner_propietario.jpg")
    st.image(img_admin, use_column_width=True)
    if st.button("🏢 ACCESO PROPIETARIO"):
        ir_a('admin')

    st.markdown("<br>", unsafe_allow_html=True)

    # Banner Catálogo
    img_mall = get_banner("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/banner_catalogo.jpg")
    st.image(img_mall, use_column_width=True)
    
    # Carga solo nombres de tiendas (Ligero)
    tiendas = supabase.table("perfiles_comercio").select("id, nombre_comercio").execute()
    for t in tiendas.data:
        if st.button(f"✨ ENTRAR A {t['nombre_comercio'].upper()}", key=t['id']):
            st.session_state.tienda_actual = t
            ir_a('tienda')

# --- VISTA 2: TIENDA (TIKTOK STYLE) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    
    # Obtenemos productos de forma eficiente
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    
    for p in prods.data:
        with st.container():
            st.markdown('<div class="video-container">', unsafe_allow_html=True)
            st.video(p['video_url'])
            st.markdown('</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([2,1])
            col1.subheader(f"{p['nombre_producto']} - ${p['precio']}")
            if col2.button("🛍️ COMPRAR", key=f"b_{p['id']}"):
                st.toast(f"Abriendo pago para {p['nombre_producto']}...")
            st.markdown("---")
    
    if st.button("🔙 VOLVER AL MALL"): ir_a('mall')

# --- VISTA 3: ADMIN (GESTIÓN RÁPIDA) ---
elif st.session_state.view == 'admin':
    st.markdown("<h2 style='color:#D4AF37;'>🚀 PANEL DE CONTROL</h2>", unsafe_allow_html=True)
    email_check = st.text_input("Confirmar Correo de Propietario")
    
    if email_check:
        perfil = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_check).execute()
        
        if perfil.data:
            com = perfil.data[0]
            tab1, tab2 = st.tabs(["📤 NUEVO VIDEO", "📦 INVENTARIO"])
            
            with tab1:
                with st.form("u_form", clear_on_submit=True):
                    n_p = st.text_input("Nombre del Producto")
                    p_p = st.number_input("Precio ($)", min_value=0.0)
                    vid = st.file_uploader("Grabar/Subir Video", type=['mp4', 'mov'])
                    if st.form_submit_button("PUBLICAR"):
                        if vid and n_p:
                            fname = f"{random.randint(100,999)}_{vid.name}"
                            path = f"videos/{com['nombre_comercio']}/{fname}"
                            supabase.storage.from_("fotos_productos").upload(path, vid.getvalue())
                            url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                            
                            supabase.table("productos").insert({
                                "nombre_producto": n_p, "precio": p_p, 
                                "video_url": url_v, "comercio_relacionado": com['nombre_comercio']
                            }).execute()
                            st.success("¡Publicado!")
                            st.rerun()

            with tab2:
                mis_prods = supabase.table("productos").select("*").eq("comercio_relacionado", com['nombre_comercio']).execute()
                for mp in mis_prods.data:
                    with st.expander(f"✏️ EDITAR: {mp['nombre_producto']}"):
                        n_pr = st.number_input("Precio", value=float(mp['precio']), key=f"p_{mp['id']}")
                        if st.button("GUARDAR", key=f"s_{mp['id']}"):
                            supabase.table("productos").update({"precio": n_pr}).eq("id", mp['id']).execute()
                            st.rerun()
                        if st.button("🗑️ BORRAR", key=f"d_{mp['id']}"):
                            supabase.table("productos").delete().eq("id", mp['id']).execute()
                            st.rerun()
    
    if st.button("🔙 SALIR"): ir_a('mall')
