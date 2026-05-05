import streamlit as st
from supabase import create_client, Client
import random

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN INSTANTÁNEA
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="centered")

@st.cache_resource
def init_connection():
    # Uso de st.secrets para mayor seguridad en tu Acer Chromebook
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Manejo de estado de navegación
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTILOS 3D LUXURY (BOTONES FLOTANTES)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; }
    
    /* Contenedor de Video estilo TikTok */
    .video-wrapper {
        position: relative;
        width: 100%;
        border-radius: 20px;
        border: 2px solid #D4AF37;
        overflow: hidden;
        margin-bottom: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    }

    /* Etiqueta de Precio 3D Flotante */
    .price-tag {
        position: absolute;
        top: 20px;
        left: 20px;
        background: linear-gradient(145deg, #D4AF37, #8B6B1E);
        color: white;
        padding: 10px 18px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 1.3rem;
        z-index: 10;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.7);
        border: 1px solid #FFD700;
    }

    /* Botón Maestro Estilo 3D */
    .stButton>button {
        background: linear-gradient(145deg, #D4AF37, #B8860B) !important;
        color: white !important;
        border-radius: 15px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        border: 1px solid #FFD700 !important;
        box-shadow: 0 6px 0 #5d4814, 0 8px 15px rgba(0,0,0,0.5) !important;
        transition: all 0.1s ease;
        height: 55px !important;
        width: 100% !important;
    }
    
    .stButton>button:active {
        box-shadow: 0 2px 0 #5d4814 !important;
        transform: translateY(4px);
    }

    /* Eliminar espacios blancos de Streamlit */
    .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VISTA: MALL (CENTRO COMERCIAL)
# ==========================================
if st.session_state.view == 'mall':
    # Imagen de marca principal (Cara de la empresa)
    logo_url = "https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg"
    st.image(logo_url, use_container_width=True)
    
    col_izq, col_der = st.columns(2)
    with col_izq:
        # Botón para que los clientes vean tiendas
        st.markdown("<h4 style='color:white; text-align:center;'>CLIENTES</h4>", unsafe_allow_html=True)
    with col_der:
        if st.button("🏢 PROPIETARIO"):
            ir_a('admin')

    st.divider()
    
    # Listado de tiendas disponibles
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    for t in tiendas.data:
        if st.button(f"✨ ENTRAR A {t['nombre_comercio'].upper()}", key=t['id']):
            st.session_state.tienda_actual = t
            ir_a('tienda')

# ==========================================
# 4. VISTA: TIENDA (VITRINA 3D)
# ==========================================
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    
    if not prods.data:
        st.warning("Esta tienda está preparando sus videos...")
    
    for p in prods.data:
        with st.container():
            # Contenedor visual del video con precio flotante incorporado
            st.markdown(f'''
                <div class="video-wrapper">
                    <div class="price-tag">${p['precio']}</div>
                </div>
            ''', unsafe_allow_html=True)
            
            st.video(p['video_url'])
            
            # Botón de compra redimensionado
            if st.button(f"🛒 COMPRAR AHORA: {p['nombre_producto']}", key=f"buy_{p['id']}"):
                st.toast(f"Contactando con {t['nombre_comercio']}...")
            st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔙 VOLVER AL MALL"): ir_a('mall')

# ==========================================
# 5. VISTA: ADMIN (CARGA Y BORRADO ACTIVO)
# ==========================================
elif st.session_state.view == 'admin':
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>🚀 PANEL DE GESTIÓN</h2>", unsafe_allow_html=True)
    email = st.text_input("Ingrese su correo de acceso", placeholder="ejemplo@correo.com")
    
    if email:
        perfil = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email).execute()
        if perfil.data:
            com = perfil.data[0]
            tab_upload, tab_stock = st.tabs(["📤 CARGA INMEDIATA", "📦 MI INVENTARIO"])
            
            with tab_upload:
                # El uso de clear_on_submit=True permite que el formulario se resetee tras cargar
                with st.form("quick_upload", clear_on_submit=True):
                    st.write("### Nuevo Producto")
                    n = st.text_input("Nombre del Producto")
                    p = st.number_input("Precio ($)", min_value=0.0, step=0.5)
                    v_file = st.file_uploader("Grabar o Subir Video Vertical", type=['mp4', 'mov'])
                    
                    submit = st.form_submit_button("🚀 PUBLICAR AHORA")
                    
                    if submit:
                        if v_file and n:
                            with st.spinner("Subiendo video a D'UNIG PLATINUM..."):
                                # 1. Subida inmediata al Storage
                                file_name = f"{random.randint(1000,9999)}_{v_file.name}"
                                path = f"videos/{com['nombre_comercio']}/{file_name}"
                                supabase.storage.from_("fotos_productos").upload(
                                    path, v_file.getvalue(), {"content-type": "video/mp4"}
                                )
                                url_final = supabase.storage.from_("fotos_productos").get_public_url(path)
                                
                                # 2. Registro en Base de Datos
                                supabase.table("productos").insert({
                                    "nombre_producto": n,
                                    "precio": p,
                                    "video_url": url_final,
                                    "comercio_relacionado": com['nombre_comercio']
                                }).execute()
                                
                                st.success(f"¡{n} ya está disponible en tu tienda!")
                                st.rerun() # Fuerza la actualización para ver el video cargado
                        else:
                            st.error("Por favor rellena el nombre y selecciona un video.")

            with tab_stock:
                st.write("### Gestionar mis productos")
                items = supabase.table("productos").select("*").eq("comercio_relacionado", com['nombre_comercio']).execute()
                
                for i in items.data:
                    c_info, c_borrar = st.columns([4, 1])
                    c_info.write(f"📦 **{i['nombre_producto']}** - ${i['precio']}")
                    
                    # BOTÓN DE BORRAR TOTALMENTE ACTIVO
                    if c_borrar.button("🗑️", key=f"del_{i['id']}"):
                        supabase.table("productos").delete().eq("id", i['id']).execute()
                        st.warning("Producto eliminado correctamente.")
                        st.rerun() # Refresco instantáneo de la lista
    
    if st.button("🔙 SALIR AL MALL"): ir_a('mall')
