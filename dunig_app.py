import streamlit as st
from supabase import create_client, Client
import random

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", page_icon="⚜️")

# --- 2. CONEXIÓN A SUPABASE (CORREGIDA) ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    
    # En lugar de usar el diccionario de opciones que da error,
    # conectamos de forma directa y simple.
    supabase: Client = create_client(url, key)
    
except Exception as e:
    st.error(f"Error de configuración: {e}")
    st.stop()

# --- 3. GESTIÓN DE ESTADOS (NAVEGACIÓN) ---
if 'pagina' not in st.session_state: 
    st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: 
    st.session_state.comercio_sesion = None
if 'comercio_seleccionado' not in st.session_state: 
    st.session_state.comercio_seleccionado = None

def navegar(destino, comercio=None):
    st.session_state.pagina = destino
    if comercio:
        st.session_state.comercio_seleccionado = comercio
    st.rerun()

# --- 4. ESTILOS VISUALES ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .card { 
        border: 1px solid #D4AF37; 
        padding: 15px; 
        border-radius: 15px; 
        background: #1A1C23; 
        text-align: center; 
        margin-bottom: 15px; 
    }
    .price { color: #D4AF37; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# LÓGICA DE PÁGINAS (FLUJO PRINCIPAL)
# ==========================================

# --- PÁGINA: INICIO ---
if st.session_state.pagina == "inicio":
    st.markdown("<h1 style='text-align:center;'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Tu centro comercial digital premium</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 ENTRAR COMO CLIENTE", use_container_width=True):
            navegar("centro_comercial")
    with col2:
        if st.button("🏢 ACCESO COMERCIOS", use_container_width=True):
            navegar("login_comercio")

# --- PÁGINA: LOGIN COMERCIO ---
elif st.session_state.pagina == "login_comercio":
    st.subheader("Acceso Propietario")
    nombre_negocio = st.text_input("Nombre de tu Negocio", placeholder="Ej: Doña Bertha")
    
    if st.button("INGRESAR AL PANEL"):
        if nombre_negocio:
            st.session_state.comercio_sesion = nombre_negocio
            navegar("panel_carga")
        else:
            st.warning("Por favor, ingresa el nombre de tu negocio.")
            
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- PÁGINA: PANEL DE CARGA (VENDEDOR) ---
elif st.session_state.pagina == "panel_carga":
    st.header(f"⚙️ Panel de Gestión: {st.session_state.comercio_sesion}")
    
    with st.form("formulario_carga", clear_on_submit=True):
        st.subheader("Subir Nuevo Producto")
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0, step=0.01)
        p_desc = st.text_area("Descripción del producto")
        
        c1, c2 = st.columns(2)
        with c1:
            foto = st.file_uploader("📸 Foto (JPG/PNG)", type=['jpg', 'png', 'jpeg'])
        with c2:
            video = st.file_uploader("🎥 Video (MP4/MOV - Máx 30s)", type=['mp4', 'mov', 'avi'])
            
        enviar = st.form_submit_button("🚀 PUBLICAR AHORA")

        if enviar:
            if p_nom and (foto or video):
                try:
                    # Limpieza de nombre para evitar error 400 (Invalid Key)
                    com_limpio = st.session_state.comercio_sesion.replace(" ", "_").replace("ñ", "n").replace("Ñ", "N")
                    random_id = random.randint(1000, 9999)
                    url_f = None
                    url_v = None

                    # Subir Imagen
                    if foto:
                        path_f = f"productos/img_{com_limpio}_{random_id}.jpg"
                        supabase.storage.from_("fotos_productos").upload(path_f, foto.getvalue())
                        url_f = supabase.storage.from_("fotos_productos").get_public_url(path_f)

                    # Subir Video
                    if video:
                        path_v = f"productos/vid_{com_limpio}_{random_id}.mp4"
                        supabase.storage.from_("fotos_productos").upload(path_v, video.getvalue())
                        url_v = supabase.storage.from_("fotos_productos").get_public_url(path_v)

                    # Guardar en Base de Datos
                    supabase.table("productos").insert({
                        "nombre_producto": p_nom,
                        "precio": p_pre,
                        "descripcion": p_desc,
                        "imagen_url": url_f,
                        "video_url": url_v,
                        "comercio_propietario": st.session_state.comercio_sesion
                    }).execute()
                    
                    st.success("✅ ¡Producto publicado exitosamente!")
                except Exception as e:
                    st.error(f"Error técnico al subir: {e}")
            else:
                st.warning("El nombre y al menos un archivo (foto/video) son obligatorios.")

    st.button("🔙 CERRAR SESIÓN", on_click=navegar, args=("inicio",))

# --- PÁGINA: CENTRO COMERCIAL (LISTA DE TIENDAS) ---
elif st.session_state.pagina == "centro_comercial":
    st.title("🏢 CENTRO COMERCIAL D'UNIG")
    
    try:
        # Traer comercios que tienen productos
        res = supabase.table("productos").select("comercio_propietario").execute()
        if res.data:
            comercios = list(set([c['comercio_propietario'] for c in res.data if c['comercio_propietario']]))
            st.subheader("Explora nuestras tiendas aliadas:")
            
            cols = st.columns(3)
            for i, tienda in enumerate(comercios):
                with cols[i % 3]:
                    st.markdown(f"<div class='card'><h3>{tienda}</h3></div>", unsafe_allow_html=True)
                    if st.button(f"Ver Vitrina de {tienda}", key=f"btn_shop_{i}"):
                        navegar("vitrina_personal", tienda)
        else:
            st.info("Aún no hay comercios registrados con productos.")
    except Exception as e:
        st.error(f"Error al cargar comercios: {e}")
        
    st.divider()
    st.button("🔙 VOLVER AL MENÚ", on_click=navegar, args=("inicio",))

# --- PÁGINA: VITRINA PERSONAL (POR TIENDA) ---
elif st.session_state.pagina == "vitrina_personal":
    tienda = st.session_state.comercio_seleccionado
    st.title(f"🏪 {tienda}")
    
    try:
        res_p = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
        
        if res_p.data:
            for p in res_p.data:
                with st.container():
                    col_a, col_b = st.columns([1, 1])
                    
                    with col_a:
                        # Prioridad al video, si no hay, muestra imagen
                        if p.get('video_url'):
                            st.video(p['video_url'])
                        elif p.get('imagen_url'):
                            st.image(p['imagen_url'], use_column_width=True)
                    
                    with col_b:
                        st.subheader(p['nombre_producto'])
                        st.markdown(f"<p class='price'>{p['precio']}$</p>", unsafe_allow_html=True)
                        if p.get('descripcion'):
                            st.write(p['descripcion'])
                        st.button("🛒 AÑADIR AL CARRITO", key=f"add_{p['id']}")
                    
                    st.divider()
        else:
            st.warning("Esta tienda no tiene productos disponibles.")
    except Exception as e:
        st.error(f"Error al cargar productos: {e}")
        
    st.button("🔙 VOLVER AL CENTRO COMERCIAL", on_click=navegar, args=("centro_comercial",))
