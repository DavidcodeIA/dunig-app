import streamlit as st
from supabase import create_client, Client
import pandas as pd
import random

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="D'UNIG PLATINUM - BETA", layout="wide")

# --- CSS LUXURY ANTIPUBLICIDAD ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0E1117; color: white; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    .card { border: 1px solid #D4AF37; padding: 20px; border-radius: 15px; background: #1A1C23; text-align: center; margin-bottom: 15px; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; border-radius: 12px; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ESTADOS ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None

def navegar(dest): 
    st.session_state.pagina = dest
    st.rerun()

# ==========================================
# 1. INICIO
# ==========================================
if st.session_state.pagina == "inicio":
    st.markdown("<h1>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Fase de Pruebas Abiertas</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='card'><h3>🛒 CLIENTE</h3><p>Ver tiendas y comprar</p></div>", unsafe_allow_html=True)
        st.button("ENTRAR A LA TIENDA", on_click=navegar, args=("cliente",))
    with c2:
        st.markdown("<div class='card'><h3>🏢 COMERCIOS</h3><p>Cargar productos gratis</p></div>", unsafe_allow_html=True)
        st.button("CARGAR MI PRODUCTO", on_click=navegar, args=("login_libre",))
    
    st.write("---")
    st.markdown("<div class='card'><h3>🤝 AFILIADOS</h3></div>", unsafe_allow_html=True)
    st.button("REGISTRO DE REFERIDOS", on_click=navegar, args=("afiliados",))

# ==========================================
# 2. ACCESO LIBRE COMERCIANTES
# ==========================================
elif st.session_state.pagina == "login_libre":
    st.markdown("<h2>🏢 ACCESO RÁPIDO COMERCIO</h2>", unsafe_allow_html=True)
    st.write("Para estas pruebas, solo ingresa el nombre de tu negocio para empezar a vender.")
    
    nom_test = st.text_input("Nombre de tu Comercio (Ej: Inversiones Platinum)")
    
    if st.button("ABRIR MI VITRINA"):
        if nom_test:
            st.session_state.comercio_sesion = nom_test
            navegar("panel_carga")
        else:
            st.warning("Escribe un nombre para identificar tus productos.")
            
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

elif st.session_state.pagina == "panel_carga":
    nombre_t = st.session_state.comercio_sesion
    st.markdown(f"<h2>🏪 Gestión de: {nombre_t}</h2>", unsafe_allow_html=True)
    
    with st.form("carga_rapida"):
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        p_img = st.text_input("Link de Imagen (URL)")
        if st.form_submit_button("🚀 PUBLICAR AHORA"):
            supabase.table("productos").insert({
                "nombre_producto": p_nom, 
                "precio": p_pre, 
                "imagen_url": p_img, 
                "comercio_propietario": nombre_t
            }).execute()
            st.success("¡Producto cargado! Ya es visible para los clientes.")
    
    st.subheader("📦 Mis Cargas Recientes")
    items = supabase.table("productos").select("*").eq("comercio_propietario", nombre_t).execute()
    if items.data:
        st.table(pd.DataFrame(items.data)[['nombre_producto', 'precio']])
    
    st.button("🏠 SALIR", on_click=navegar, args=("inicio",))

# ==========================================
# 3. VITRINA CLIENTE (FUNCIONES COMPLETAS)
# ==========================================
elif st.session_state.pagina == "cliente":
    st.markdown("<h1>🛍️ SHOPPING D'UNIG</h1>", unsafe_allow_html=True)
    
    # Selector de Tienda Dinámico
    res_c = supabase.table("productos").select("comercio_propietario").execute()
    lista_t = list(set([x['comercio_propietario'] for x in res_c.data if x['comercio_propietario']]))
    
    if lista_t:
        t_sel = st.selectbox("🏬 Selecciona un comercio para ver sus productos:", lista_t)
        
        prods = supabase.table("productos").select("*").eq("comercio_propietario", t_sel).execute()
        cols = st.columns(2)
        for idx, p in enumerate(prods.data):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class='card'>
                    <img src='{p['imagen_url'] if p['imagen_url'] else 'https://via.placeholder.com/150'}' style='width:100%; border-radius:10px;'>
                    <h4>{p['nombre_producto']}</h4>
                    <p style='color:#D4AF37; font-size:20px;'><b>{p['precio']}$</b></p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Añadir ➕", key=f"v_{p['id']}"):
                    st.session_state.carrito.append({'nombre': p['nombre_producto'], 'precio': p['precio'], 'comercio': t_sel})
                    st.toast("Añadido al carrito")

    # Pago y GPS
    if st.session_state.carrito:
        st.write("---")
        total = sum(i['precio'] for i in st.session_state.carrito)
        st.markdown(f"### Total a Pagar: {total}$")
        
        ref = st.text_input("Nro Referencia")
        nom_cli = st.text_input("Tu Nombre")
        
        # GPS AUTOMÁTICO
        st.markdown("""
            <button onclick="navigator.geolocation.getCurrentPosition(p => {
                const link = `https://www.google.com/maps?q=${p.coords.latitude},${p.coords.longitude}`;
                window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'gps_val', value: link}, '*');
            }, e => alert('Activa tu GPS'))" 
            style="width:100%; height:45px; border-radius:12px; background:#D4AF37; font-weight:bold; border:none; color:black;">
            📍 CAPTURAR MI DIRECCIÓN GPS
            </button>
        """, unsafe_allow_html=True)
        
        dir_gps = st.text_input("Link Ubicación:", key="gps_val")
        
        if st.button("🔥 FINALIZAR PEDIDO"):
            if ref and nom_cli and dir_gps:
                st.balloons()
                st.success("¡Pedido enviado con éxito!")
                st.session_state.carrito = []
            else:
                st.warning("Completa los datos de pago y ubicación.")

    st.button("🏠 VOLVER", on_click=navegar, args=("inicio",))

# ==========================================
# 4. AFILIADOS
# ==========================================
elif st.session_state.pagina == "afiliados":
    st.markdown("<h2>🤝 REGISTRO DE AFILIADOS</h2>", unsafe_allow_html=True)
    a_nom = st.text_input("Nombre")
    a_em = st.text_input("Correo")
    if st.button("OBTENER CÓDIGO"):
        cod = f"DG-{random.randint(1000,9999)}"
        st.success(f"Bienvenido. Tu código es: {cod}")
    
    st.button("🏠 VOLVER", on_click=navegar, args=("inicio",))
