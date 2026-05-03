import streamlit as st
from supabase import create_client, Client
import random

# --- 1. CONFIGURACIÓN E INSTALACIÓN ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")

# --- 2. CONEXIÓN SEGURA ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- 3. ESTADOS DE NAVEGACIÓN ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None
if 'comercio_seleccionado' not in st.session_state: st.session_state.comercio_seleccionado = None

def navegar(destino, comercio=None):
    st.session_state.pagina = destino
    if comercio:
        st.session_state.comercio_seleccionado = comercio
    st.rerun()

# --- 4. ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .card { border: 1px solid #D4AF37; padding: 15px; border-radius: 15px; background: #1A1C23; text-align: center; margin-bottom: 15px; }
    .btn-comercio { background: #262730; border: 1px solid #D4AF37; padding: 20px; border-radius: 15px; cursor: pointer; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# LÓGICA DE PÁGINAS
# ==========================================

# --- PÁGINA INICIAL ---
if st.session_state.pagina == "inicio":
    st.title("⚜️ BIENVENIDOS A D'UNIG PLATINUM ⚜️")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 ENTRAR COMO CLIENTE", use_container_width=True):
            navegar("centro_comercial")
    with col2:
        if st.button("🏢 ACCESO COMERCIOS", use_container_width=True):
            navegar("login_comercio")

# --- LOGIN COMERCIO ---
elif st.session_state.pagina == "login_comercio":
    st.subheader("Acceso Propietario")
    nombre = st.text_input("Nombre de tu Negocio")
    if st.button("ENTRAR AL PANEL"):
        if nombre:
            st.session_state.comercio_sesion = nombre
            navegar("panel_carga")
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- PANEL DE CARGA ---
elif st.session_state.pagina == "panel_carga":
    st.header(f"🏪 Panel de {st.session_state.comercio_sesion}")
    
    with st.form("carga_producto", clear_on_submit=True):
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        p_desc = st.text_area("Descripción corta")
        foto = st.file_uploader("📸 Foto del producto", type=['jpg', 'png', 'jpeg'])
        enviar = st.form_submit_button("🚀 PUBLICAR")

        if enviar:
            if p_nom and foto:
                try:
                    # Limpiar nombre para evitar error 400
                    nombre_limpio = st.session_state.comercio_sesion.replace(" ", "_")
                    ext = foto.name.split('.')[-1]
                    path_foto = f"productos/{nombre_limpio}_{random.randint(100,999)}.{ext}"

                    # Subir foto
                    supabase.storage.from_("fotos_productos").upload(path=path_foto, file=foto.getvalue())
                    url_foto = supabase.storage.from_("fotos_productos").get_public_url(path_foto)

                    # Guardar en tabla
                    supabase.table("productos").insert({
                        "nombre_producto": p_nom,
                        "precio": p_pre,
                        "descripcion": p_desc,
                        "imagen_url": url_foto,
                        "comercio_propietario": st.session_state.comercio_sesion
                    }).execute()
                    st.success("¡Producto cargado!")
                except Exception as e:
                    st.error(f"Error al cargar: {e}")
            else:
                st.warning("Faltan datos obligatorios.")
    
    st.button("🏠 SALIR", on_click=navegar, args=("inicio",))

# --- CENTRO COMERCIAL (LISTA DE TIENDAS) ---
elif st.session_state.pagina == "centro_comercial":
    st.title("🏢 CENTRO COMERCIAL D'UNIG")
    
    # Obtener nombres únicos de comercios
    res = supabase.table("productos").select("comercio_propietario").execute()
    if res.data:
        comercios = list(set([c['comercio_propietario'] for c in res.data]))
        st.subheader("Selecciona una tienda para ver su vitrina:")
        
        cols = st.columns(3)
        for idx, tienda in enumerate(comercios):
            with cols[idx % 3]:
                st.markdown(f"<div class='card'><h3>{tienda}</h3></div>", unsafe_allow_html=True)
                if st.button(f"Entrar a {tienda}", key=f"t_{tienda}"):
                    navegar("vitrina_personal", tienda)
    else:
        st.info("Aún no hay tiendas registradas.")
    
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- VITRINA PERSONAL ---
elif st.session_state.pagina == "vitrina_personal":
    tienda = st.session_state.comercio_seleccionado
    st.title(f"🏪 Tienda: {tienda}")
    
    res = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
    if res.data:
        cols = st.columns(2)
        for idx, p in enumerate(res.data):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class='card'>
                    <img src="{p['imagen_url']}" style="width:100%; height:180px; object-fit:cover; border-radius:10px;">
                    <h4>{p['nombre_producto']}</h4>
                    <p style='color:gray; font-size:12px;'>{p.get('descripcion', '')}</p>
                    <h3 style='color:#D4AF37;'>{p['precio']}$</h3>
                </div>
                """, unsafe_allow_html=True)
                st.button("🛒 Pedir", key=f"btn_{p['id']}")
    
    st.button("🔙 VOLVER AL CENTRO COMERCIAL", on_click=navegar, args=("centro_comercial",))
