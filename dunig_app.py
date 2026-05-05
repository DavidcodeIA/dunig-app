import streamlit as st
from supabase import create_client, Client
import random

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="centered")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Inicialización de estados
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTILOS DORADOS 3D Y PERSONALIZADOS
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; }
    
    /* Contenedor de Video */
    .video-wrapper {
        position: relative;
        width: 100%;
        border-radius: 25px;
        border: 3px solid #D4AF37;
        overflow: hidden;
        margin-bottom: 10px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.9);
    }

    /* Botón de Precio Dorado Flotante */
    .floating-price-gold {
        position: absolute;
        top: 20px;
        right: 20px;
        background: linear-gradient(145deg, #FFD700, #D4AF37);
        color: #000;
        padding: 12px 20px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.4rem;
        z-index: 10;
        border: 2px solid #FFF;
        box-shadow: 0 4px 15px rgba(212, 175, 55, 0.6);
        text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
    }

    /* Botones de Streamlit estilo 3D */
    .stButton>button {
        background: linear-gradient(145deg, #D4AF37, #B8860B) !important;
        color: white !important;
        border-radius: 15px !important;
        font-weight: bold !important;
        border: 1px solid #FFD700 !important;
        box-shadow: 0 5px 0 #5d4814 !important;
        transition: all 0.1s ease;
    }
    
    .stButton>button:active {
        box-shadow: 0 2px 0 #5d4814 !important;
        transform: translateY(3px);
    }

    /* Estilo para el Sidebar */
    [data-testid="stSidebar"] {
        background-color: #111;
        border-right: 2px solid #D4AF37;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. MENÚ LATERAL (SIDEBAR)
# ==========================================
with st.sidebar:
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg", width=150)
    st.markdown("<h2 style='color:#D4AF37;'>MENÚ PLATINUM</h2>", unsafe_allow_html=True)
    st.divider()
    
    if st.button("🏠 IR AL MALL", use_container_width=True):
        ir_a('mall')
    
    if st.button("⚙️ PANEL DE CONTROL", use_container_width=True):
        ir_a('admin')
    
    st.divider()
    st.caption("D'UNIG PLATINUM © 2026")

# ==========================================
# 4. VISTAS DE LA APLICACIÓN
# ==========================================

# --- VISTA: MALL ---
if st.session_state.view == 'mall':
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg", use_container_width=True)
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>CENTRO COMERCIAL</h1>", unsafe_allow_html=True)
    
    # Buscador con Lupa
    busqueda = st.text_input("🔍 Buscar productos o tiendas...", placeholder="Ej: Zapatos, D'Unig...")
    
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    for t in tiendas.data:
        if busqueda.lower() in t['nombre_comercio'].lower():
            if st.button(f"✨ ENTRAR A {t['nombre_comercio'].upper()}", key=t['id'], use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA: TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    
    # Flecha ir atrás y título
    col_atras, col_tit = st.columns([1, 5])
    if col_atras.button("⬅️"): ir_a('mall')
    col_tit.markdown(f"<h2 style='color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    
    # Filtro de búsqueda dentro de la tienda
    query = st.text_input("🔍 Buscar en esta tienda...", key="search_tienda")
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    
    for p in prods.data:
        if query.lower() in p['nombre_producto'].lower():
            st.markdown(f'''
                <div class="video-wrapper">
                    <div class="floating-price-gold">${p['precio']}</div>
                </div>
            ''', unsafe_allow_html=True)
            st.video(p['video_url'])
            
            if st.button(f"🛒 COMPRAR: {p['nombre_producto']}", key=f"buy_{p['id']}", use_container_width=True):
                st.info(f"💳 DATOS DE PAGO:\n\n{t.get('datos_pago', 'Solicitar al vendedor')}")

# --- VISTA: ADMIN ---
elif st.session_state.view == 'admin':
    # Flecha atrás
    if st.button("⬅️ VOLVER"): ir_a('mall')
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>🚀 GESTIÓN DE NEGOCIO</h2>", unsafe_allow_html=True)
    
    email = st.text_input("Correo de Propietario")
    if email:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email).execute()
        if res.data:
            com = res.data[0]
            t1, t2, t3 = st.tabs(["📤 CARGAR", "📦 STOCK", "💰 DATOS PAGO"])
            
            with t1:
                with st.form("carga_rapida", clear_on_submit=True):
                    nom = st.text_input("Nombre del Producto")
                    pre = st.number_input("Precio ($)", min_value=0.0)
                    vid = st.file_uploader("Video Vertical", type=['mp4', 'mov'])
                    if st.form_submit_button("🚀 PUBLICAR"):
                        if vid and nom:
                            path = f"videos/{com['nombre_comercio']}/{random.randint(100,999)}_{vid.name}"
                            supabase.storage.from_("fotos_productos").upload(path, vid.getvalue())
                            url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                            supabase.table("productos").insert({"nombre_producto": nom, "precio": pre, "video_url": url_v, "comercio_relacionado": com['nombre_comercio']}).execute()
                            st.success("¡Publicado!")
                            st.rerun()

            with t2:
                items = supabase.table("productos").select("*").eq("comercio_relacionado", com['nombre_comercio']).execute()
                for i in items.data:
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**{i['nombre_producto']}** - ${i['precio']}")
                    if c2.button("🗑️", key=f"del_{i['id']}"):
                        supabase.table("productos").delete().eq("id", i['id']).execute()
                        st.rerun()
            
            with t3:
                st.write("### Configura cómo te pagan")
                nuevo_pago = st.text_area("Escribe tus datos (Banco, Pago Móvil, Zelle, etc.)", value=com.get('datos_pago', ''))
                if st.button("💾 GUARDAR DATOS DE PAGO"):
                    supabase.table("perfiles_comercio").update({"datos_pago": nuevo_pago}).eq("id", com['id']).execute()
                    st.success("Datos actualizados.")
