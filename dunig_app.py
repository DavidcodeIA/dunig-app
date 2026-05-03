import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONFIGURACIÓN LUXURY ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")

# --- BLOQUEO DE PUBLICIDAD Y ESTILO DORADO ---
st.markdown("""
    <style>
    /* Ocultar elementos de Streamlit (Publicidad/Menús) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}
    
    /* Fondo y Colores D'UNIG */
    .stApp { background-color: #0E1117; color: white; }
    h1, h2, h3, h4 { color: #D4AF37 !important; text-align: center; font-family: 'serif'; }
    
    /* Tarjetas de Producto Luxury */
    .product-card {
        border: 1px solid #D4AF37; 
        padding: 15px; 
        border-radius: 20px;
        background: #1A1C23; 
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.1);
    }
    
    /* Botones Dorados */
    .stButton>button { 
        background-color: #D4AF37; 
        color: black; 
        font-weight: bold; 
        border-radius: 12px; 
        width: 100%;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover { background-color: #FACD67; border: none; color: black; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN BASE DE DATOS ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ESTADOS DE NAVEGACIÓN ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'comercio_actual' not in st.session_state: st.session_state.comercio_actual = None

# --- FUNCIONES DE ACCIÓN RÁPIDA ---
def navegar(destino): st.session_state.pagina = destino
def add_to_cart(n, p, c): 
    st.session_state.carrito.append({'nombre': n, 'precio': p, 'comercio': c})
    st.toast(f"🛒 {n} añadido")

# ==========================================
# 1. LANDING PAGE (INICIO)
# ==========================================
if st.session_state.pagina == "inicio":
    st.markdown("<h1>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='product-card'><h2>🛒 COMPRAR</h2><p>Tienda Luxury</p></div>", unsafe_allow_html=True)
        st.button("ENTRAR A LA TIENDA", on_click=navegar, args=("cliente",))
    with col2:
        st.markdown("<div class='product-card'><h2>🏢 COMERCIOS</h2><p>Panel Administrativo</p></div>", unsafe_allow_html=True)
        st.button("GESTIONAR MI NEGOCIO", on_click=navegar, args=("login_comercio",))

# ==========================================
# 2. PANEL DE COMERCIO (INVENTARIO Y CARGA)
# ==========================================
elif st.session_state.pagina == "login_comercio":
    st.markdown("<h2>🔑 ACCESO COMERCIANTE</h2>", unsafe_allow_html=True)
    user_com = st.text_input("Nombre de tu Comercio")
    pass_com = st.text_input("Contraseña", type="password")
    if st.button("ENTRAR AL PANEL"):
        if pass_com == "admin123": # Puedes personalizar esta clave
            st.session_state.comercio_actual = user_com
            navegar("panel_comercio")
            st.rerun()
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

elif st.session_state.pagina == "panel_comercio":
    st.header(f"🏪 Gestión de {st.session_state.comercio_actual}")
    
    tab1, tab2 = st.tabs(["➕ Cargar Producto", "📦 Mi Inventario"])
    
    with tab1:
        with st.form("carga_prod"):
            nom = st.text_input("Nombre del Producto")
            pre = st.number_input("Precio Venta ($)", min_value=0.0)
            img = st.text_input("URL de la Imagen (Link)")
            cat = st.selectbox("Categoría", ["Comida", "Ropa", "Servicios", "Otros"])
            if st.form_submit_button("🚀 PUBLICAR EN VITRINA"):
                supabase.table("productos").insert({
                    "nombre_producto": nom, "precio": pre, 
                    "imagen_url": img, "categoria": cat,
                    "comercio_propietario": st.session_state.comercio_actual
                }).execute()
                st.success("¡Producto cargado con éxito!")
    
    with tab2:
        st.subheader("Productos actuales en tu tienda")
        res_inv = supabase.table("productos").select("*").eq("comercio_propietario", st.session_state.comercio_actual).execute()
        if res_inv.data:
            df = pd.DataFrame(res_inv.data)
            st.dataframe(df[['nombre_producto', 'precio', 'categoria']], use_container_width=True)
            if st.button("🗑️ Limpiar todo el inventario"):
                supabase.table("productos").delete().eq("comercio_propietario", st.session_state.comercio_actual).execute()
                st.rerun()
        else:
            st.info("No tienes productos cargados.")
            
    st.button("🏠 CERRAR SESIÓN", on_click=navegar, args=("inicio",))

# ==========================================
# 3. MÓDULO CLIENTE (VITRINA Y GPS)
# ==========================================
elif st.session_state.pagina == "cliente":
    st.markdown("<h1>🛍️ SHOPPING D'UNIG</h1>", unsafe_allow_html=True)
    
    # Selector de Tienda
    res_coms = supabase.table("productos").select("comercio_propietario").execute()
    lista_tiendas = list(set([p['comercio_propietario'] for p in res_coms.data if p['comercio_propietario']]))
    
    if lista_tiendas:
        tienda_sel = st.selectbox("🏬 Elige una tienda:", lista_tiendas)
        
        # Vitrina
        res_p = supabase.table("productos").select("*").eq("comercio_propietario", tienda_sel).execute()
        cols = st.columns(2)
        for idx, p in enumerate(res_p.data):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class='product-card'>
                    <img src='{p['imagen_url'] if p['imagen_url'] else 'https://via.placeholder.com/150'}' style='width:100%; border-radius:10px;'>
                    <h4>{p['nombre_producto']}</h4>
                    <p style='color:#D4AF37; font-size:18px;'><b>{p['precio']}$</b></p>
                </div>
                """, unsafe_allow_html=True)
                st.button(f"Añadir ➕", key=f"btn_{p['id']}", on_click=add_to_cart, args=(p['nombre_producto'], p['precio'], tienda_sel))

    # Carrito y Pago
    if st.session_state.carrito:
        st.markdown("---")
        st.markdown("### 🛒 Tu Pedido")
        total = sum(i['precio'] for i in st.session_state.carrito)
        st.markdown(f"## Total: {total}$")
        
        ref = st.text_input("🔢 Nro. Referencia Bancaria (Requerido)")
        nom_c = st.text_input("👤 Tu Nombre completo")
        
        # BOTÓN GPS AUTOMÁTICO
        st.markdown("""
            <button onclick="navigator.geolocation.getCurrentPosition(p => {
                const link = `https://www.google.com/maps?q=${p.coords.latitude},${p.coords.longitude}`;
                window.parent.postMessage({type: 'streamlit:set_widget_value', key: 'gps_val', value: link}, '*');
            }, e => alert('Activa el GPS'))" 
            style="width:100%; height:45px; border-radius:10px; background:#D4AF37; border:none; font-weight:bold;">
            📍 CAPTURAR MI DIRECCIÓN GPS
            </button>
        """, unsafe_allow_html=True)
        
        dir_gps = st.text_input("Ubicación capturada:", key="gps_val")
        
        if st.button("🔥 FINALIZAR COMPRA"):
            if ref and nom_c and dir_gps:
                resumen = ", ".join([i['nombre'] for i in st.session_state.carrito])
                supabase.table("pedidos").insert({
                    "cliente": nom_c, "productos": resumen, "total": total, 
                    "direccion": dir_gps, "nro_referencia": ref, "comercio_destino": st.session_state.carrito[0]['comercio']
                }).execute()
                st.balloons()
                st.success("¡Pedido enviado! El comercio verificará tu pago.")
                st.session_state.carrito = []
                st.rerun()
            else:
                st.warning("⚠️ Faltan datos (Referencia, Nombre o GPS).")

    st.button("🏠 VOLVER AL INICIO", on_click=navegar, args=("inicio",))
