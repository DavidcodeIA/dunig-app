import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ESTADOS Y NAVEGACIÓN ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None

def navegar(dest): 
    st.session_state.pagina = dest
    st.rerun()

# ==========================================
# PANEL DE CARGA (CORREGIDO PARA BUCKETS)
# ==========================================
if st.session_state.pagina == "panel_carga":
    st.header(f"🏪 Panel: {st.session_state.comercio_sesion}")
    
    with st.container():
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        foto = st.file_uploader("📸 Foto del producto", type=['jpg', 'png', 'jpeg'])
        
        if st.button("🚀 PUBLICAR"):
            if p_nom and foto:
                try:
                    # 1. Subir la imagen al Bucket de Supabase
                    file_path = f"public/{random.randint(1000,9999)}_{foto.name}"
                    # Nota: Importar random si no está
                    import random
                    
                    # Subida al storage
                    storage_res = supabase.storage.from_("fotos_productos").upload(
                        path=file_path,
                        file=foto.getvalue(),
                        file_options={"content-type": foto.type}
                    )
                    
                    # 2. Obtener la URL pública de esa foto
                    img_url = supabase.storage.from_("fotos_productos").get_public_url(file_path)
                    
                    # 3. Guardar en la tabla de productos
                    supabase.table("productos").insert({
                        "nombre_producto": p_nom, 
                        "precio": p_pre, 
                        "imagen_url": img_url,
                        "comercio_propietario": st.session_state.comercio_sesion
                    }).execute()
                    
                    st.success("✅ ¡Producto y foto cargados con éxito!")
                except Exception as e:
                    st.error(f"Error al subir: {e}")
            else:
                st.warning("Faltan datos o la foto.")
    
    st.button("🏠 SALIR", on_click=navegar, args=("inicio",))

# ==========================================
# VITRINA CLIENTE (MOSTRAR IMAGEN)
# ==========================================
elif st.session_state.pagina == "cliente":
    st.title("🛍️ VITRINA D'UNIG")
    
    prods = supabase.table("productos").select("*").execute()
    if prods.data:
        cols = st.columns(2)
        for idx, p in enumerate(prods.data):
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="border:1px solid #D4AF37; padding:10px; border-radius:15px; background:#1A1C23; text-align:center; margin-bottom:10px;">
                    <img src="{p['imagen_url']}" style="width:100%; border-radius:10px; height:180px; object-fit:cover;">
                    <h4 style="color:white;">{p['nombre_producto']}</h4>
                    <p style="color:#D4AF37; font-weight:bold;">{p['precio']}$</p>
                </div>
                """, unsafe_allow_html=True)
                st.button(f"Comprar", key=f"btn_{p['id']}")
    else:
        st.info("Aún no hay productos cargados.")
    
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- MANTENER RESTO DE PÁGINAS (INICIO, LOGIN, ETC) ---
