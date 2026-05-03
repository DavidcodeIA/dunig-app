import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONFIGURACIÓN LUXURY ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")

# --- ESTILO CSS MEJORADO (LANDING PAGE) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #0E1117; }
    .role-card {
        border: 2px solid #D4AF37; padding: 25px; border-radius: 20px;
        background: #1A1C23; text-align: center; cursor: pointer;
        transition: 0.3s; height: 200px; display: flex; flex-direction: column; justify-content: center;
    }
    .role-card:hover { transform: translateY(-10px); background: #252830; }
    h1, h2, h3 { color: #D4AF37 !important; font-family: 'serif'; text-align: center; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; border-radius: 10px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- INICIALIZACIÓN DE ESTADOS ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'carrito' not in st.session_state: st.session_state.carrito = []

# --- FUNCIONES DE NAVEGACIÓN ---
def navegar(destino): st.session_state.pagina = destino

# ==========================================
# PÁGINA DE INICIO (LANDING PAGE)
# ==========================================
if st.session_state.pagina == "inicio":
    st.markdown("<h1>⚜️ BIENVENIDO A D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: white !important;'>Selecciona tu portal de acceso</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        st.markdown("<div class='role-card'><h2>🛒 CLIENTE</h2><p>Realiza tus compras luxury</p></div>", unsafe_allow_html=True)
        if st.button("ENTRAR A COMPRAR", key="btn_cliente"): navegar("cliente")

    with col2:
        st.markdown("<div class='role-card'><h2>🏢 COMERCIO</h2><p>Gestionar inventario y ventas</p></div>", unsafe_allow_html=True)
        if st.button("ACCESO COMERCIANTE", key="btn_comercio"): navegar("login_comercio")

    with col3:
        st.markdown("<div class='role-card'><h2>🚚 REPARTIDOR</h2><p>Panel de entregas pendientes</p></div>", unsafe_allow_html=True)
        if st.button("ACCESO DELIVERY", key="btn_reparto"): navegar("login_repartidor")

    with col4:
        st.markdown("<div class='role-card'><h2>🤝 AFILIADOS</h2><p>Gana dinero recomendando</p></div>", unsafe_allow_html=True)
        if st.button("PROGRAMA AFILIADOS", key="btn_afiliado"): navegar("afiliados")

# ==========================================
# SEGURIDAD: LOGINS
# ==========================================
elif st.session_state.pagina == "login_comercio":
    st.markdown("<h2>🔑 ACCESO COMERCIANTE</h2>", unsafe_allow_html=True)
    pw = st.text_input("Contraseña de Comercio", type="password")
    if st.button("INGRESAR"):
        if pw == "admin123": navegar("comercio") # Cambia esta clave
        else: st.error("Clave incorrecta")
    if st.button("🔙 VOLVER"): navegar("inicio")

elif st.session_state.pagina == "login_repartidor":
    st.markdown("<h2>🔑 ACCESO REPARTIDOR</h2>", unsafe_allow_html=True)
    pw = st.text_input("Contraseña de Repartidor", type="password")
    if st.button("INGRESAR"):
        if pw == "delivery123": navegar("repartidor") # Cambia esta clave
        else: st.error("Clave incorrecta")
    if st.button("🔙 VOLVER"): navegar("inicio")

# ==========================================
# MÓDULO: CLIENTE (CON REFERENCIA BANCARIA)
# ==========================================
elif st.session_state.pagina == "cliente":
    if st.sidebar.button("🏠 VOLVER AL INICIO"): navegar("inicio")
    
    # ... (Aquí va tu código de Vitrina que ya tenemos) ...
    # Al momento del pago, añadimos la casilla de referencia:
    
    st.markdown("### 🏦 DETALLES DE PAGO")
    st.info("Pago Móvil: 0102 - 04121234567 - V-12345678")
    referencia = st.text_input("🔢 Número de Referencia Bancaria (6 dígitos)")
    nombre_c = st.text_input("👤 Tu Nombre")
    dir_c = st.text_input("📍 Dirección")
    
    if st.button("🔥 FINALIZAR PEDIDO"):
        if referencia and nombre_c:
            # Aquí guardas en la DB incluyendo el campo referencia
            st.success(f"¡Gloria a Dios! Pedido enviado. Referencia: {referencia}")
            st.session_state.carrito = []
            st.balloons()
        else:
            st.warning("⚠️ La referencia bancaria es obligatoria para validar tu pago.")

# ==========================================
# MÓDULO: PROGRAMA DE AFILIADOS
# ==========================================
elif st.session_state.pagina == "afiliados":
    st.markdown("<h1>🤝 PROGRAMA DE AFILIADOS</h1>", unsafe_allow_html=True)
    st.write("Gana el 5% de cada venta que refieras a D'UNIG PLATINUM.")
    st.text_input("Ingresa tu correo para generar tu link:")
    if st.button("GENERAR MI CÓDIGO"):
        st.success("Tu código de afiliado es: DUNIG-GOLD-2026")
    if st.button("🏠 VOLVER"): navegar("inicio")

# Mantenemos las lógicas de 'comercio' y 'repartidor' en sus respectivas condiciones...
