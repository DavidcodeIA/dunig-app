import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA LUXURY ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILO CSS DORADO LUXURY ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    h1, h2, h3, h4 { color: #D4AF37 !important; text-align: center; font-family: 'serif'; }
    .stButton>button { 
        background-color: #D4AF37; color: #000000; 
        border-radius: 12px; font-weight: bold; border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #FACD67; transform: scale(1.02); }
    .product-card { 
        border: 1px solid #D4AF37; padding: 15px; border-radius: 20px; 
        background: #1A1C23; text-align: center; margin-bottom: 15px;
    }
    .stTextInput>div>div>input { background-color: #1A1C23; color: white; border: 1px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A BASE DE DATOS ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- INICIALIZACIÓN DE ESTADOS (VITAL PARA EVITAR ERRORES) ---
if 'carrito' not in st.session_state:
    st.session_state.carrito = []
if 'checkout' not in st.session_state:
    st.session_state.checkout = False

# --- FUNCIONES DE ACCIÓN INSTANTÁNEA (UN SOLO CLIC) ---
def add_to_cart(nombre, precio):
    st.session_state.carrito.append({'nombre': nombre, 'precio': precio})
    st.toast(f"✨ {nombre} añadido")

def go_to_checkout():
    st.session_state.checkout = True

def cancel_checkout():
    st.session_state.checkout = False

# --- MENÚ DE NAVEGACIÓN (Esto evita el NameError) ---
st.sidebar.markdown("<h2 style='color: #D4AF37;'>⚜️ MENÚ</h2>", unsafe_allow_html=True)
perfil = st.sidebar.radio("IR A:", ["🛒 Vitrina Cliente", "🏢 Panel Comerciante", "🚚 Repartidor"])

# ==========================================
# PERFIL: CLIENTE (FLUJO LUXURY)
# ==========================================
if perfil == "🛒 Vitrina Cliente":
    
    if st.session_state.checkout:
        # --- PANTALLA DE PAGO ---
        st.markdown("<h1>🏦 FINALIZAR PEDIDO</h1>", unsafe_allow_html=True)
        
        total = sum(item['precio'] for item in st.session_state.carrito)
        
        col_pay1, col_pay2 = st.columns([2, 1])
        with col_pay1:
            st.markdown(f"<div style='background:#1A1C23; padding:20px; border-radius:15px; border:1px solid #D4AF37;'>", unsafe_allow_html=True)
            st.subheader("Tu Pedido")
            for i in st.session_state.carrito:
                st.write(f"🔸 {i['nombre']} — **{i['precio']}$**")
            st.markdown(f"<h2 style='color:#D4AF37;'>Total a Pagar: {total}$</h2>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_pay2:
            st.info("💎 **PAGO MÓVIL DUEÑO**\n\nBVC (0102)\n0412-1234567\nV-12.345.678\n\n*Envía el capture al recibir.*")

        st.write("---")
        nombre_c = st.text_input("👤 Tu Nombre")
        
        # Botón de ubicación (Simulado para rapidez)
        if st.button("📍 CAPTURAR MI UBICACIÓN GPS"):
            st.session_state.loc = "Ubicación detectada: Calle Principal, Edif. Platinum"
            
        dir_c = st.text_input("📍 Dirección Confirmada", value=st.session_state.get('loc', ""))

        c1, c2 = st.columns(2)
        if c1.button("🔥 CONFIRMAR COMPRA"):
            if nombre_c and dir_c:
                resumen = ", ".join([i['nombre'] for i in st.session_state.carrito])
                supabase.table("pedidos").insert({
                    "cliente": nombre_c, "productos": resumen, "total": total, "direccion": dir_c
                }).execute()
                st.balloons()
                st.success("¡GLORIA A DIOS! Pedido enviado con éxito.")
                st.session_state.carrito = []
                st.session_state.checkout = False
                st.button("Hacer otra compra", on_click=st.rerun)
        
        c2.button("⬅️ VOLVER A VITRINA", on_click=cancel_checkout)

    else:
        # --- PANTALLA DE VITRINA ---
        st.markdown("<h1>⚜️ VITRINA D'UNIG ⚜️</h1>", unsafe_allow_html=True)
        
        if st.session_state.carrito:
            t_actual = sum(i['precio'] for i in st.session_state.carrito)
            st.button(f"🛒 PAGAR MI ORDEN ({t_actual}$)", on_click=go_to_checkout)

        try:
            res = supabase.table("productos").select("*").execute()
            prods = res.data
            if prods:
                grid = st.columns(2)
                for idx, p in enumerate(prods):
                    with grid[idx % 2]:
                        st.markdown(f"""
                        <div class="product-card">
                            <img src="{p['imagen_url'] if p['imagen_url'] else 'https://via.placeholder.com/150'}" style="width:100%; border-radius:10px;">
                            <h4>{p['nombre_producto']}</h4>
                            <p style="font-size:20px; font-weight:bold; color:#D4AF37;">{p['precio']}$</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.button(f"Añadir ➕", key=f"b_{p['id']}_{idx}", 
                                  on_click=add_to_cart, args=(p['nombre_producto'], p['precio']))
            else:
                st.info("Surtiendo la vitrina luxury...")
        except Exception as e:
            st.error(f"Error: {e}")

# ==========================================
# OTROS PERFILES (Mantenemos la lógica previa)
# ==========================================
elif perfil == "🏢 Panel Comerciante":
    st.header("🏢 Gestión de Inventario")
    # ... (Tu código de carga de productos aquí)
    st.info("Usa este panel para cargar nuevos productos a la vitrina.")

elif perfil == "🚚 Repartidor":
    st.header("🚚 Entregas Pendientes")
    # ... (Tu código de visualización de pedidos aquí)
    st.info("Aquí aparecerán los pedidos confirmados por los clientes.")
