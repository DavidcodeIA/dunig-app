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
elif st.session_state.pagina == "panel_carga":
    st.header(f"🏪 Panel de {st.session_state.comercio_sesion}")
    
    # Usamos un formulario para agrupar todo
    with st.form("carga_producto", clear_on_submit=True):
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        p_desc = st.text_area("Descripción (detalles del producto)")
        
        col_f, col_v = st.columns(2)
        with col_f:
            foto = st.file_uploader("📸 Foto", type=['jpg', 'png', 'jpeg'])
        with col_v:
            video = st.file_uploader("🎥 Video corto (Máx 30s)", type=['mp4', 'mov', 'avi'])
        
        enviar = st.form_submit_button("🚀 PUBLICAR PRODUCTO")

        if enviar:
            if p_nom and (foto or video):
                try:
                    nom_c = st.session_state.comercio_sesion.replace(" ", "_")
                    id_rand = random.randint(1000, 9999)
                    url_foto = None
                    url_video = None

                    # Subir Foto si existe
                    if foto:
                        path_f = f"productos/img_{nom_c}_{id_rand}.jpg"
                        supabase.storage.from_("fotos_productos").upload(path_f, foto.getvalue())
                        url_foto = supabase.storage.from_("fotos_productos").get_public_url(path_f)

                    # Subir Video si existe
                    if video:
                        path_v = f"productos/vid_{nom_c}_{id_rand}.mp4"
                        supabase.storage.from_("fotos_productos").upload(path_v, video.getvalue())
                        url_video = supabase.storage.from_("fotos_productos").get_public_url(path_v)

                    # GUARDAR EN TABLA (Asegúrate de haber corrido el SQL en Supabase antes)
                    supabase.table("productos").insert({
                        "nombre_producto": p_nom,
                        "precio": p_pre,
                        "descripcion": p_desc,
                        "imagen_url": url_foto,
                        "video_url": url_video,
                        "comercio_propietario": st.session_state.comercio_sesion
                    }).execute()
                    
                    st.success("✅ ¡Multimedia cargada con éxito!")
                except Exception as e:
                    st.error(f"Error técnico: {e}")
            else:
                st.warning("Escribe el nombre y sube al menos una foto o video.")

# --- DENTRO DEL PANEL DE CARGA ---
with st.form("carga_producto", clear_on_submit=True):
    p_nom = st.text_input("Nombre del Producto")
    p_pre = st.number_input("Precio ($)", min_value=0.0)
    p_desc = st.text_area("Descripción corta")
    
    col_med1, col_med2 = st.columns(2)
    with col_med1:
        foto = st.file_uploader("📸 Foto", type=['jpg', 'png', 'jpeg'])
    with col_med2:
        video = st.file_uploader("🎥 Video (Máx 30s)", type=['mp4', 'mov', 'avi'])
    
    enviar = st.form_submit_button("🚀 PUBLICAR PRODUCTO")

    if enviar:
        if p_nom and (foto or video): # Al menos uno de los dos
            try:
                nom_c = st.session_state.comercio_sesion.replace(" ", "_")
                id_random = random.randint(100, 999)
                url_foto = None
                url_video = None

                # --- SUBIR FOTO ---
                if foto:
                    path_f = f"productos/img_{nom_c}_{id_random}.jpg"
                    supabase.storage.from_("fotos_productos").upload(path_f, foto.getvalue())
                    url_foto = supabase.storage.from_("fotos_productos").get_public_url(path_f)

                # --- SUBIR VIDEO ---
                if video:
                    path_v = f"productos/vid_{nom_c}_{id_random}.mp4"
                    supabase.storage.from_("fotos_productos").upload(path_v, video.getvalue())
                    url_video = supabase.storage.from_("fotos_productos").get_public_url(path_v)

                # --- GUARDAR EN TABLA ---
                supabase.table("productos").insert({
                    "nombre_producto": p_nom,
                    "precio": p_pre,
                    "descripcion": p_desc,
                    "imagen_url": url_foto,
                    "video_url": url_video, # Nueva columna
                    "comercio_propietario": st.session_state.comercio_sesion
                }).execute()
                
                st.success("✅ ¡Producto con multimedia cargado!")
            except Exception as e:
                st.error(f"Error técnico: {e}")
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
