import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONFIGURACIÓN LUXURY ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .role-card {
        border: 2px solid #D4AF37; padding: 20px; border-radius: 15px;
        background: #1A1C23; text-align: center; margin-bottom: 10px;
    }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ESTADOS INICIALES ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'comercio_actual' not in st.session_state: st.session_state.comercio_actual = None

# --- FUNCIONES DE ACCIÓN INSTANTÁNEA ---
def set_pagina(dest): st.session_state.pagina = dest
def add_prod(n, p, c): 
    st.session_state.carrito.append({'nombre': n, 'precio': p, 'comercio': c})
    st.toast(f"✅ {n} añadido")

# ==========================================
# LANDING PAGE
# ==========================================
if st.session_state.pagina == "inicio":
    st.markdown("<h1>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='role-card'><h2>🛒 COMPRAR</h2></div>", unsafe_allow_html=True)
        st.button("ENTRAR A LA TIENDA", on_click=set_pagina, args=("cliente",))
    with c2:
        st.markdown("<div class='role-card'><h2>🏢 COMERCIOS</h2></div>", unsafe_allow_html=True)
        st.button("GESTIONAR MI TIENDA", on_click=set_pagina, args=("login_comercio",))

# ==========================================
# MÓDULO COMERCIO (CARGA DE PRODUCTOS)
# ==========================================
elif st.session_state.pagina == "login_comercio":
    st.subheader("Acceso Administrativo")
    user_com = st.text_input("Nombre de tu Comercio (Ej: Pizza Real)")
    pass_com = st.text_input("Contraseña", type="password")
    if st.button("INGRESAR AL PANEL"):
        if pass_com == "admin123": 
            st.session_state.comercio_actual = user_com
            set_pagina("panel_comercio")
            st.rerun()
    st.button("🔙 VOLVER", on_click=set_pagina, args=("inicio",))

elif st.session_state.pagina == "panel_comercio":
    st.header(f"🏪 Panel de {st.session_state.comercio_actual}")
    with st.expander("➕ Cargar Nuevo Producto", expanded=True):
        nom = st.text_input("Nombre del Producto")
        pre = st.number_input("Precio ($)", min_value=0.0)
        img = st.text_input("URL de Imagen")
        if st.button("PUBLICAR PRODUCTO"):
            supabase.table("productos").insert({
                "nombre_producto": nom, "precio": pre, 
                "imagen_url": img, "comercio_propietario": st.session_state.comercio_actual
            }).execute()
            st.success("¡Producto en vitrina!")
    st.button("🏠 SALIR", on_click=set_pagina, args=("inicio",))

# ==========================================
# MÓDULO CLIENTE (VITRINA POR TIENDAS)
# ==========================================
elif st.session_state.pagina == "cliente":
    st.markdown("<h1>🛍️ CENTRO COMERCIAL D'UNIG</h1>", unsafe_allow_html=True)
    
    # 1. Obtener lista de comercios con productos
    res_com = supabase.table("productos").select("comercio_propietario").execute()
    lista_comercios = list(set([p['comercio_propietario'] for p in res_com.data if p['comercio_propietario']]))
    
    if lista_comercios:
        tienda_sel = st.selectbox("🏬 Selecciona una Tienda para ver sus productos:", lista_comercios)
        
        # 2. Mostrar productos de esa tienda
        res_p = supabase.table("productos").select("*").eq("comercio_propietario", tienda_sel).execute()
        cols = st.columns(2)
        for idx, p in enumerate(res_p.data):
            with cols[idx % 2]:
                st.markdown(f"<div class='role-card'><img src='{p['imagen_url']}' style='width:100%'><h4>{p['nombre_producto']}</h4><b>{p['precio']}$</b></div>", unsafe_allow_html=True)
                st.button(f"Añadir ➕", key=f"p_{p['id']}", on_click=add_prod, args=(p['nombre_producto'], p['precio'], tienda_sel))
    
    # 3. Carrito y Pago
    if st.session_state.carrito:
        st.write("---")
        st.subheader("🛒 Tu Carrito")
        total = sum(i['precio'] for i in st.session_state.carrito)
        st.markdown(f"### Total: {total}$")
        
        ref = st.text_input("🔢 Nro de Referencia Bancaria")
        nom_c = st.text_input("👤 Tu Nombre")
        
        # BOTÓN GPS (Usando HTML5 Geolocation)
        st.markdown("""
            <button onclick="navigator.geolocation.getCurrentPosition(pos => {
                const url = `https://www.google.com/maps?q=${pos.coords.latitude},${pos.coords.longitude}`;
                window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'gps_val', value: url}, '*');
                alert('📍 Ubicación capturada con éxito');
            }, err => alert('Por favor activa el GPS de tu teléfono'))" 
            style="width:100%; height:40px; border-radius:10px; background:#D4AF37; font-weight:bold;">
            📍 MARCAR MI DIRECCIÓN GPS (TIEMPO REAL)
            </button>
        """, unsafe_allow_html=True)
        
        # Captura el valor enviado por el JS
        dir_gps = st.text_input("📍 Link de ubicación capturado:", key="gps_val")
        
        if st.button("🔥 FINALIZAR PEDIDO"):
            if ref and nom_c and dir_gps:
                supabase.table("pedidos").insert({
                    "cliente": nom_c, "productos": str(st.session_state.carrito),
                    "total": total, "direccion": dir_gps, "nro_referencia": ref
                }).execute()
                st.balloons()
                st.success("¡Pedido enviado! Dios te bendiga.")
                st.session_state.carrito = []
                st.rerun()
            else: st.warning("Completa Referencia, Nombre y Ubicación GPS")
            
    st.button("🏠 VOLVER AL INICIO", on_click=set_pagina, args=("inicio",))
