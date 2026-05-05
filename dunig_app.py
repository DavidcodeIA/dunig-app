import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="centered")

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.stop()

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTILOS VISUALES (SIN TÍTULOS)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; }
    
    /* Imagen de fondo tipo Banner */
    .banner-img {
        width: 100%;
        border-radius: 15px;
        border: 2px solid #D4AF37;
        margin-bottom: 10px;
    }

    /* Contenedor de botones sobre imagen */
    .img-button {
        position: relative;
        cursor: pointer;
        transition: transform 0.3s;
    }
    .img-button:hover { transform: scale(1.02); }

    .stButton>button {
        background: linear-gradient(90deg, #D4AF37, #8B6B1E) !important;
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================

# --- VISTA 1: MALL (CENTRO COMERCIAL VISUAL) ---
if st.session_state.view == 'mall':
    # Foto Principal 1: Acceso Propietario
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/banner_propietario.jpg", use_column_width=True)
    if st.button("🏢 GESTIONAR MI NEGOCIO", use_container_width=True):
        ir_a('admin')

    st.markdown("<br>", unsafe_allow_html=True)

    # Foto Principal 2: Ver Catálogo
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/banner_catalogo.jpg", use_column_width=True)
    
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    for t in tiendas.data:
        if st.button(f"✨ ENTRAR A {t['nombre_comercio'].upper()}", key=t['id'], use_container_width=True):
            st.session_state.tienda_actual = t
            ir_a('tienda')

# --- VISTA 2: TIENDA (TIKTOK STYLE) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    
    for p in prods.data:
        with st.container():
            st.video(p['video_url'])
            col_p, col_b = st.columns([2,1])
            col_p.subheader(f"{p['nombre_producto']} - ${p['precio']}")
            if col_b.button("🛍️ COMPRAR", key=f"buy_{p['id']}"):
                # Aquí llamarías a la función ventana_pago definida anteriormente
                st.info("Función de pago activada")
            st.markdown("---")
    
    if st.button("🔙 VOLVER"): ir_a('mall')

# --- VISTA 3: ADMIN (GESTIÓN TOTAL) ---
elif st.session_state.view == 'admin':
    st.markdown("<h2 style='color:#D4AF37;'>🚀 PANEL DE CONTROL</h2>", unsafe_allow_html=True)
    email_check = st.text_input("Confirmar Correo de Propietario")
    
    perfil = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_check).execute()
    
    if perfil.data:
        com = perfil.data[0]
        tab1, tab2 = st.tabs(["📤 CARGAR VIDEO", "📦 GESTIONAR INVENTARIO"])
        
        with tab1:
            with st.form("upload_form"):
                n_p = st.text_input("Nombre del Producto")
                p_p = st.number_input("Precio ($)", min_value=0.0)
                s_p = st.number_input("Stock Inicial", min_value=0)
                vid = st.file_uploader("Grabar Video", type=['mp4', 'mov'])
                if st.form_submit_button("PUBLICAR"):
                    # Lógica de subida a Storage...
                    st.success("Cargando...")

        with tab2:
            st.subheader("Lista de Productos")
            mis_prods = supabase.table("productos").select("*").eq("comercio_relacionado", com['nombre_comercio']).execute()
            
            for mp in mis_prods.data:
                with st.expander(f"🖼️ {mp['nombre_producto']} - ${mp['precio']}"):
                    new_price = st.number_input("Nuevo Precio", value=float(mp['precio']), key=f"pr_{mp['id']}")
                    new_stock = st.number_input("Stock", value=int(mp.get('stock', 0)), key=f"st_{mp['id']}")
                    
                    c1, c2 = st.columns(2)
                    if c1.button("💾 ACTUALIZAR", key=f"up_{mp['id']}"):
                        supabase.table("productos").update({"precio": new_price, "stock": new_stock}).eq("id", mp['id']).execute()
                        st.success("Actualizado")
                        st.rerun()
                    
                    if c2.button("🗑️ ELIMINAR", key=f"del_{mp['id']}"):
                        supabase.table("productos").delete().eq("id", mp['id']).execute()
                        st.warning("Eliminado")
                        st.rerun()
    
    if st.button("🔙 SALIR"): ir_a('mall')
