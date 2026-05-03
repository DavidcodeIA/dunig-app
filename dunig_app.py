import streamlit as st
from supabase import create_client, Client
import pandas as pd
import base64 # Para procesar la imagen local

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")

# --- CSS LUXURY ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0E1117; color: white; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    .card { border: 1px solid #D4AF37; padding: 15px; border-radius: 15px; background: #1A1C23; text-align: center; margin-bottom: 15px; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; border-radius: 10px; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ESTADOS ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None

def navegar(dest): 
    st.session_state.pagina = dest
    st.rerun()

# ==========================================
# 1. INICIO
# ==========================================
if st.session_state.pagina == "inicio":
    st.markdown("<h1>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='card'><h3>🛒 CLIENTE</h3></div>", unsafe_allow_html=True)
        st.button("VER TIENDA", on_click=navegar, args=("cliente",))
    with c2:
        st.markdown("<div class='card'><h3>🏢 COMERCIOS</h3></div>", unsafe_allow_html=True)
        st.button("SUBIR PRODUCTO", on_click=navegar, args=("login_libre",))

# ==========================================
# 2. PANEL DE CARGA CON SUBIDA DIRECTA
# ==========================================
elif st.session_state.pagina == "login_libre":
    st.markdown("<h2>🏢 ACCESO COMERCIO</h2>", unsafe_allow_html=True)
    nom_test = st.text_input("Nombre de tu Negocio")
    if st.button("CONFIGURAR VITRINA"):
        if nom_test:
            st.session_state.comercio_sesion = nom_test
            navegar("panel_carga")
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

elif st.session_state.pagina == "panel_carga":
    nombre_t = st.session_state.comercio_sesion
    st.markdown(f"<h2>🏪 Panel: {nombre_t}</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        
        # --- FUNCIÓN DE SUBIDA DIRECTA ---
        foto = st.file_uploader("📸 Selecciona la foto del producto", type=['jpg', 'png', 'jpeg'])
        
        if st.button("🚀 PUBLICAR PRODUCTO"):
            if p_nom and foto:
                # Convertimos la imagen a Base64 para guardarla en la base de datos
                bytes_data = foto.getvalue()
                base64_image = base64.b64encode(bytes_data).decode('utf-8')
                img_final = f"data:image/jpeg;base64,{base64_image}"
                
                supabase.table("productos").insert({
                    "nombre_producto": p_nom, 
                    "precio": p_pre, 
                    "imagen_url": img_final, # Ahora guardamos el contenido de la imagen, no un link
                    "comercio_propietario": nombre_t
                }).execute()
                st.success("¡Producto cargado exitosamente!")
            else:
                st.warning("Por favor rellena el nombre y selecciona una foto.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.button("🏠 FINALIZAR", on_click=navegar, args=("inicio",))

# ==========================================
# 3. VITRINA CLIENTE
# ==========================================
elif st.session_state.pagina == "cliente":
    st.markdown("<h1>🛍️ SHOPPING D'UNIG</h1>", unsafe_allow_html=True)
    
    res_c = supabase.table("productos").select("comercio_propietario").execute()
    lista_t = list(set([x['comercio_propietario'] for x in res_c.data if x['comercio_propietario']]))
    
    if lista_t:
        t_sel = st.selectbox("🏬 Selecciona un comercio:", lista_t)
        prods = supabase.table("productos").select("*").eq("comercio_propietario", t_sel).execute()
        
        cols = st.columns(2)
        for idx, p in enumerate(prods.data):
            with cols[idx % 2]:
                # Mostramos la imagen extraída del dispositivo
                st.markdown(f"""
                <div class='card'>
                    <img src='{p['imagen_url']}' style='width:100%; height:150px; object-fit:cover; border-radius:10px;'>
                    <h4>{p['nombre_producto']}</h4>
                    <p style='color:#D4AF37; font-size:20px;'><b>{p['precio']}$</b></p>
                </div>
                """, unsafe_allow_html=True)
                st.button(f"Añadir ➕", key=f"v_{p['id']}")

    st.button("🏠 VOLVER", on_click=navegar, args=("inicio",))
