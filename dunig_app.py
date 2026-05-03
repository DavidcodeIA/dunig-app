import streamlit as st
from supabase import create_client, Client
import pandas as pd
import random
import string

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")

# --- CSS LUXURY ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0E1117; color: white; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; border-radius: 12px; width: 100%; border: none; }
    .card { border: 1px solid #D4AF37; padding: 20px; border-radius: 15px; background: #1A1C23; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ESTADOS ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'user_auth' not in st.session_state: st.session_state.user_auth = None

def navegar(dest): 
    st.session_state.pagina = dest
    st.rerun()

# ==========================================
# 1. LANDING PAGE
# ==========================================
if st.session_state.pagina == "inicio":
    st.markdown("<h1>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='card'><h3>🛒 CLIENTE</h3></div>", unsafe_allow_html=True)
        st.button("ENTRAR A COMPRAR", on_click=navegar, args=("cliente",))
    with col2:
        st.markdown("<div class='card'><h3>🏢 COMERCIOS</h3></div>", unsafe_allow_html=True)
        st.button("MI PANEL / REGISTRO", on_click=navegar, args=("login_comercio",))
    
    st.write("---")
    st.markdown("<div class='card'><h3>🤝 AFILIADOS</h3></div>", unsafe_allow_html=True)
    st.button("PROGRAMA DE REFERIDOS", on_click=navegar, args=("afiliados",))

# ==========================================
# 2. SISTEMA DE COMERCIOS (ACCESO Y REGISTRO)
# ==========================================
elif st.session_state.pagina == "login_comercio":
    st.markdown("<h2>🏢 ACCESO COMERCIANTE</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrar mi Negocio"])
    
    with t2:
        st.write("Registra tu correo y recibe tu clave instantánea.")
        em_reg = st.text_input("Correo Electrónico")
        nom_com = st.text_input("Nombre de la Tienda")
        if st.button("OBTENER MI CLAVE PLATINUM"):
            if em_reg and nom_com:
                try:
                    clave = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    supabase.table("perfiles_comercios").insert({
                        "email": em_reg, "nombre_comercio": nom_com, "clave_acceso": clave
                    }).execute()
                    st.success(f"¡REGISTRADO! Tu clave es: **{clave}**")
                    st.info("Copia esta clave y úsala en la pestaña 'Iniciar Sesión'.")
                except: st.error("Este correo ya está registrado.")
    
    with t1:
        em_in = st.text_input("Correo")
        pw_in = st.text_input("Clave", type="password")
        if st.button("ENTRAR AL PANEL DE CARGA"):
            res = supabase.table("perfiles_comercios").select("*").eq("email", em_in).eq("clave_acceso", pw_in).execute()
            if res.data:
                st.session_state.user_auth = res.data[0]
                navegar("panel_carga")
            else: st.error("Datos incorrectos.")
    
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

elif st.session_state.pagina == "panel_carga":
    nombre_t = st.session_state.user_auth['nombre_comercio']
    st.markdown(f"<h2>🏪 Panel: {nombre_t}</h2>", unsafe_allow_html=True)
    
    with st.expander("➕ PUBLICAR NUEVO PRODUCTO", expanded=True):
        p_nom = st.text_input("Nombre")
        p_pre = st.number_input("Precio $", min_value=0.0)
        p_img = st.text_input("Link de Imagen")
        if st.button("SUBIR A LA VITRINA"):
            supabase.table("productos").insert({
                "nombre_producto": p_nom, "precio": p_pre, 
                "imagen_url": p_img, "comercio_propietario": nombre_t
            }).execute()
            st.toast("¡Producto en vivo!")
            st.rerun()

    st.subheader("📦 Mi Inventario")
    inv = supabase.table("productos").select("*").eq("comercio_propietario", nombre_t).execute()
    if inv.data: st.dataframe(pd.DataFrame(inv.data)[['nombre_producto', 'precio']])
    
    st.button("🏠 CERRAR SESIÓN", on_click=navegar, args=("inicio",))

# ==========================================
# 3. HOJA DE AFILIADOS (REGISTRO Y CONTROL)
# ==========================================
elif st.session_state.pagina == "afiliados":
    st.markdown("<h2>🤝 PROGRAMA DE AFILIADOS</h2>", unsafe_allow_html=True)
    
    with st.form("reg_af"):
        st.write("Únete y gana comisiones.")
        a_nom = st.text_input("Nombre")
        a_em = st.text_input("Correo")
        if st.form_submit_button("UNIRSE AL EQUIPO"):
            cod = f"DG-{random.randint(100,999)}"
            supabase.table("afiliados").insert({"nombre_afiliado": a_nom, "email_afiliado": a_em, "codigo_referido": cod}).execute()
            st.success(f"¡Bienvenido! Tu código es: {cod}")
            
    st.write("---")
    if st.text_input("Acceso Admin Afiliados", type="password") == "afiliados2026":
        data = supabase.table("afiliados").select("*").execute()
        if data.data: st.table(pd.DataFrame(data.data))
    
    st.button("🏠 VOLVER", on_click=navegar, args=("inicio",))

# ==========================================
# 4. VITRINA CLIENTE (MANTIENE TODO LO ANTERIOR)
# ==========================================
elif st.session_state.pagina == "cliente":
    # (Aquí pones el código de la vitrina, el carrito, el GPS y el Nro de Referencia)
    # Asegúrate de usar 'comercio_propietario' para mostrar los productos de cada dueño.
    st.button("🏠 VOLVER AL INICIO", on_click=navegar, args=("inicio",))
