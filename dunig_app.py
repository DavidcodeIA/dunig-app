import streamlit as st
from supabase import create_client, Client
import pandas as pd
import random
import string

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")

# --- CSS LUXURY ANTIPUBLICIDAD ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0E1117; color: white; }
    .card { border: 2px solid #D4AF37; padding: 20px; border-radius: 15px; background: #1A1C23; text-align: center; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; border-radius: 10px; width: 100%; }
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

def navegar(dest): st.session_state.pagina = dest

# ==========================================
# 1. LANDING PAGE
# ==========================================
if st.session_state.pagina == "inicio":
    st.markdown("<h1>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    cols = st.columns(2)
    with cols[0]:
        st.markdown("<div class='card'><h3>🛒 COMPRAR</h3></div>", unsafe_allow_html=True)
        st.button("ENTRAR", on_click=navegar, args=("cliente",))
    with cols[1]:
        st.markdown("<div class='card'><h3>🏢 COMERCIOS</h3></div>", unsafe_allow_html=True)
        st.button("MI VITRINA", on_click=navegar, args=("login_comercio",))
    
    st.write("---")
    st.markdown("<div class='card'><h3>🤝 PROGRAMA DE AFILIADOS</h3></div>", unsafe_allow_html=True)
    st.button("REGISTRARSE COMO AFILIADO", on_click=navegar, args=("registro_afiliados",))

# ==========================================
# 2. SISTEMA DE COMERCIOS (REGISTRO Y CARGA)
# ==========================================
elif st.session_state.pagina == "login_comercio":
    st.subheader("Acceso a Vitrina Personalizada")
    
    tab1, tab2 = st.tabs(["Ingresar", "Registrar mi Comercio"])
    
    with tab2:
        with st.form("reg_com"):
            email_reg = st.text_input("Tu Correo Electrónico")
            nombre_com = st.text_input("Nombre del Negocio")
            if st.form_submit_button("REGISTRAR Y RECIBIR CLAVE"):
                clave_gen = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                supabase.table("perfiles_comercios").insert({
                    "email": email_reg, "nombre_comercio": nombre_com, "clave_acceso": clave_gen
                }).execute()
                st.success(f"¡Registro Exitoso! Tu clave de acceso es: **{clave_gen}** (Guárdala bien)")

    with tab1:
        email_in = st.text_input("Correo")
        pass_in = st.text_input("Clave enviada", type="password")
        if st.button("ENTRAR A MI PANEL"):
            res = supabase.table("perfiles_comercios").select("*").eq("email", email_in).eq("clave_acceso", pass_in).execute()
            if res.data:
                st.session_state.user_auth = res.data[0]
                navegar("panel_control")
                st.rerun()
            else: st.error("Datos incorrectos")
    
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

elif st.session_state.pagina == "panel_control":
    comercio = st.session_state.user_auth['nombre_comercio']
    st.header(f"🏪 Vitrina de {comercio}")
    
    # CARGA DE PRODUCTOS
    with st.expander("➕ Cargar Nuevo Producto", expanded=True):
        with st.form("new_p"):
            n = st.text_input("Nombre")
            p = st.number_input("Precio $", min_value=0.0)
            img = st.text_input("Link Imagen")
            if st.form_submit_button("PUBLICAR AL INSTANTE"):
                supabase.table("productos").insert({
                    "nombre_producto": n, "precio": p, "imagen_url": img, "comercio_propietario": comercio
                }).execute()
                st.toast("✅ Publicado en la vitrina del cliente")
    
    # INVENTARIO
    st.subheader("📦 Mis Productos")
    items = supabase.table("productos").select("*").eq("comercio_propietario", comercio).execute()
    if items.data:
        st.table(pd.DataFrame(items.data)[['nombre_producto', 'precio']])
    
    st.button("🏠 CERRAR SESIÓN", on_click=navegar, args=("inicio",))

# ==========================================
# 3. SISTEMA DE AFILIADOS (LA HOJA DE CONTROL)
# ==========================================
elif st.session_state.pagina == "registro_afiliados":
    st.header("🤝 Programa de Afiliados D'UNIG")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Regístrate")
        nom_af = st.text_input("Nombre Completo")
        em_af = st.text_input("Correo")
        if st.button("GENERAR CÓDIGO DE AFILIADO"):
            cod = f"D-GOLD-{random.randint(100,999)}"
            supabase.table("afiliados").insert({
                "nombre_afiliado": nom_af, "email_afiliado": em_af, "codigo_referido": cod
            }).execute()
            st.success(f"Bienvenido. Tu código es: {cod}")

    with col_b:
        st.subheader("📊 Hoja de Control (Admin)")
        if st.text_input("Clave de Auditor", type="password") == "afiliados2026":
            hoja = supabase.table("afiliados").select("*").execute()
            if hoja.data: st.dataframe(pd.DataFrame(hoja.data))
    
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# ==========================================
# 4. VITRINA DEL CLIENTE (MANTIENE TODAS LAS FUNCIONES)
# ==========================================
elif st.session_state.pagina == "cliente":
    st.title("🛍️ SHOPPING D'UNIG")
    # (Aquí va el código de la vitrina con GPS, carrito y referencia bancaria que ya perfeccionamos)
    # Incluye el filtro por tienda para que el cliente elija a quién comprar.
    st.button("🔙 VOLVER AL INICIO", on_click=navegar, args=("inicio",))
