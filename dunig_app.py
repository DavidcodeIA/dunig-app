import streamlit as st
from supabase import create_client, Client
import random

# --- CONFIGURACIÓN Y CONEXIÓN ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ESTADOS DE NAVEGACIÓN ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None

def navegar(dest, comercio=None):
    st.session_state.pagina = dest
    if comercio: st.session_state.comercio_sel = comercio
    st.rerun()

# ==========================================
# 1. TIENDA GENERAL (PANEL DE COMERCIOS)
# ==========================================
if st.session_state.pagina == "cliente":
    st.markdown("<h1>🏢 CENTRO COMERCIAL D'UNIG</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["✨ Vitrina General", "🏪 Explorar Tiendas"])
    
    with tabs[0]:
        st.subheader("Todos los Productos")
        res = supabase.table("productos").select("*").execute()
        cols = st.columns(3)
        for idx, p in enumerate(res.data):
            with cols[idx % 3]:
                st.markdown(f"""
                <div style="border:1px solid #D4AF37; padding:10px; border-radius:15px; background:#1A1C23; text-align:center; margin-bottom:10px;">
                    <img src="{p['imagen_url']}" style="width:100%; height:150px; object-fit:cover; border-radius:10px;">
                    <p><b>{p['nombre_producto']}</b></p>
                    <p style="color:#D4AF37;">{p['precio']}$</p>
                </div>
                """, unsafe_allow_html=True)

    with tabs[1]:
        st.subheader("Nuestros Aliados")
        # Aquí buscamos los comercios únicos
        comercios = supabase.table("productos").select("comercio_propietario").execute()
        lista_c = list(set([c['comercio_propietario'] for c in comercios.data]))
        
        cols_c = st.columns(4)
        for idx, nom_c in enumerate(lista_c):
            with cols_c[idx % 4]:
                st.markdown(f"""
                <div style="text-align:center; border:1px solid #555; padding:15px; border-radius:50%; width:120px; height:120px; margin:auto; background:#262730; display:flex; align-items:center; justify-content:center;">
                    <b style="color:#D4AF37;">{nom_c[:2].upper()}</b>
                </div>
                <p style="text-align:center; margin-top:10px;"><b>{nom_c}</b></p>
                """, unsafe_allow_html=True)
                if st.button(f"Ver {nom_c}", key=f"shop_{nom_c}"):
                    navegar("vitrina_personal", nom_c)

    st.button("🔙 VOLVER AL INICIO", on_click=navegar, args=("inicio",))

# ==========================================
# 2. VITRINA PERSONAL (POR TIENDA)
# ==========================================
elif st.session_state.pagina == "vitrina_personal":
    tienda = st.session_state.comercio_sel
    st.markdown(f"<h1>🏪 {tienda.upper()}</h1>", unsafe_allow_html=True)
    
    # Filtramos solo los productos de esta tienda
    res_p = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
    
    if res_p.data:
        cols = st.columns(2)
        for idx, p in enumerate(res_p.data):
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="border:1px solid #D4AF37; padding:10px; border-radius:15px; background:#1A1C23; text-align:center; margin-bottom:10px;">
                    <img src="{p['imagen_url']}" style="width:100%; height:200px; object-fit:cover; border-radius:10px;">
                    <h3>{p['nombre_producto']}</h3>
                    <h2 style="color:#D4AF37;">{p['precio']}$</h2>
                </div>
                """, unsafe_allow_html=True)
                st.button("Añadir al Carrito 🛒", key=f"cart_{p['id']}")
    else:
        st.warning("Esta tienda aún no tiene productos.")
        
    st.button("🔙 VOLVER AL CENTRO COMERCIAL", on_click=navegar, args=("cliente",))

# ==========================================
# 3. PANEL DE CARGA (LOGOS Y PRODUCTOS)
# ==========================================
elif st.session_state.pagina == "panel_carga":
    st.header(f"⚙️ Configuración: {st.session_state.comercio_sesion}")
    
    with st.expander("📸 Subir Producto Nuevo", expanded=True):
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        foto = st.file_uploader("Foto del producto", type=['jpg','png','jpeg'])
        
        if st.button("🚀 PUBLICAR"):
            if p_nom and foto:
                # (Aquí va tu lógica de limpieza de nombre y subida que ya funciona)
                st.success("¡Producto cargado!")
    
    st.button("🔙 SALIR", on_click=navegar, args=("inicio",))
