import streamlit as st
from supabase import create_client, Client
import pandas as pd
import random  # <--- Vital para que no de pantalla negra
import string

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CONEXIÓN (Asegúrate de tener estos nombres en Secrets) ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Error de conexión. Verifica tus Secrets en Streamlit Cloud.")

# --- 3. CSS LUXURY (OCULTA MENÚS Y PONE DORADO) ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0E1117; color: white; }
    .card { border: 1px solid #D4AF37; padding: 15px; border-radius: 15px; background: #1A1C23; text-align: center; margin-bottom: 15px; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; border-radius: 10px; width: 100%; border: none; height: 45px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GESTIÓN DE PÁGINAS ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None
if 'carrito' not in st.session_state: st.session_state.carrito = []

def navegar(dest):
    st.session_state.pagina = dest
    st.rerun()

# ==========================================
# PÁGINA: INICIO
# ==========================================
if st.session_state.pagina == "inicio":
    st.markdown("<h1>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='card'><h3>🛒 CLIENTE</h3></div>", unsafe_allow_html=True)
        st.button("VER VITRINA", on_click=navegar, args=("cliente",))
    with col2:
        st.markdown("<div class='card'><h3>🏢 COMERCIOS</h3></div>", unsafe_allow_html=True)
        st.button("CARGAR PRODUCTOS", on_click=navegar, args=("acceso_comercio",))

# ==========================================
# PÁGINA: ACCESO COMERCIO (PRUEBAS LIBRES)
# ==========================================
elif st.session_state.pagina == "acceso_comercio":
    st.markdown("<h2>🏢 PANEL DE CONTROL</h2>", unsafe_allow_html=True)
    nombre = st.text_input("Nombre de tu Negocio")
    if st.button("ENTRAR AL PANEL"):
        if nombre:
            st.session_state.comercio_sesion = nombre
            navegar("panel_carga")
        else:
            st.warning("Escribe el nombre de tu negocio.")
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# ==========================================
# PÁGINA: PANEL DE CARGA (CON SUBIDA DE FOTO)
# ==========================================
elif st.session_state.pagina == "panel_carga":
    st.header(f"🏪 Cargando para: {st.session_state.comercio_sesion}")
    
    with st.container():
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        foto = st.file_uploader("📸 Foto del producto", type=['jpg', 'png', 'jpeg'])
        
# --- DENTRO DE PANEL DE CARGA ---
if st.button("🚀 PUBLICAR AHORA"):
    if p_nom and foto:
        try:
            # 1. Limpiamos el nombre del comercio para el archivo (quitar espacios y ñ)
            comercio_seguro = st.session_state.comercio_sesion.replace(" ", "_").replace("ñ", "n").replace("Ñ", "N")
            
            # 2. Generar nombre único y seguro
            ext = foto.name.split('.')[-1]
            nombre_archivo = f"{comercio_seguro}_{random.randint(1000,9999)}.{ext}"
            path_en_bucket = f"productos/{nombre_archivo}"

            # 3. Subir al Storage
            supabase.storage.from_("fotos_productos").upload(
                path=path_en_bucket,
                file=foto.getvalue(),
                file_options={"content-type": foto.type, "x-upsert": "true"}
            )

            # 4. Obtener URL Pública
            url_res = supabase.storage.from_("fotos_productos").get_public_url(path_en_bucket)
            
            # 5. Guardar en la Tabla
            supabase.table("productos").insert({
                "nombre_producto": p_nom,
                "precio": p_pre,
                "imagen_url": url_res,
                "comercio_propietario": st.session_state.comercio_sesion
            }).execute()
            
            st.success("✅ ¡Publicado con éxito!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Error técnico: {e}")

# ==========================================
# PÁGINA: VITRINA CLIENTE
# ==========================================
elif st.session_state.pagina == "cliente":
    st.markdown("<h1>🛍️ VITRINA D'UNIG</h1>", unsafe_allow_html=True)
    
    try:
        res = supabase.table("productos").select("*").execute()
        if res.data:
            cols = st.columns(2)
            for idx, p in enumerate(res.data):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class='card'>
                        <img src="{p['imagen_url']}" style="width:100%; height:180px; object-fit:cover; border-radius:10px;">
                        <h4>{p['nombre_producto']}</h4>
                        <p style="color:#D4AF37; font-size:18px;"><b>{p['precio']}$</b></p>
                        <p style="font-size:12px; color:gray;">Tienda: {p['comercio_propietario']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.button("Añadir 🛒", key=f"btn_{p['id']}")
        else:
            st.info("No hay productos disponibles por ahora.")
    except Exception as e:
        st.error("Error al cargar la vitrina.")
    
    st.button("🏠 VOLVER", on_click=navegar, args=("inicio",))
