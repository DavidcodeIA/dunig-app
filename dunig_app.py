import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="D'UNIG PLATINUM - MultiApp", layout="wide")

# --- ESTÉTICA SIN PUBLICIDAD ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #0E1117; color: #D4AF37; }
    .stButton>button { background-color: #D4AF37; color: black; border-radius: 8px; font-weight: bold; width: 100%; }
    .product-card { border: 1px solid #D4AF37; padding: 15px; border-radius: 15px; background: #1A1C23; margin-bottom: 20px; }
    h1, h2, h3 { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- INICIALIZAR CARRITO ---
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- BARRA LATERAL (NAVEGACIÓN) ---
st.sidebar.title("⚜️ D'UNIG PLATINUM")
perfil = st.sidebar.radio("MODO DE ACCESO:", ["🛒 Vitrina Cliente", "🏢 Panel Comerciante", "🚚 Repartidor"])

# ==========================================
# PERFIL: CLIENTE (VITRINA Y COMPRA)
# ==========================================
if perfil == "🛒 Vitrina Cliente":
    st.title("🛍️ Nuestra Vitrina")
    
    # Mostrar Carrito flotante en la lateral
    with st.sidebar.expander(f"🛒 Mi Carrito ({len(st.session_state.carrito)})", expanded=True):
        if not st.session_state.carrito:
            st.write("Tu carrito está vacío.")
        else:
            total_pagar = 0
            resumen_texto = ""
            for i, item in enumerate(st.session_state.carrito):
                st.write(f"- {item['nombre']} (${item['precio']})")
                total_pagar += item['precio']
                resumen_texto += f"{item['nombre']} (${item['precio']}), "
            
            st.write("---")
            st.subheader(f"Total: {total_pagar} $")
            
            direccion = st.text_input("📍 Dirección de entrega")
            nombre_c = st.text_input("👤 Tu nombre")
            
            if st.button("🚀 FINALIZAR PEDIDO"):
                if direccion and nombre_c:
                    data_pedido = {
                        "cliente": nombre_c,
                        "productos": resumen_texto,
                        "total": total_pagar,
                        "direccion": direccion
                    }
                    supabase.table("pedidos").insert(data_pedido).execute()
                    st.success("¡Pedido enviado! El repartidor va en camino.")
                    st.session_state.carrito = [] # Limpiar carrito
                    st.rerun()
                else:
                    st.error("Faltan datos de entrega.")

    # Cargar Productos de la DB
    try:
        res = supabase.table("productos").select("*").execute()
        productos = res.data
        if productos:
            cols = st.columns(3)
            for i, p in enumerate(productos):
                with cols[i % 3]:
                    st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
                    if p['imagen_url']:
                        st.image(p['imagen_url'], use_container_width=True)
                    st.subheader(p['nombre_producto'])
                    st.write(f"🏷️ **Precio:** {p['precio']} $")
                    st.write(f"🏢 **Tienda:** {p['comercio_nombre']}")
                    if st.button(f"Añadir al Carrito", key=f"p_{p['id']}"):
                        st.session_state.carrito.append({'nombre': p['nombre_producto'], 'precio': p['precio']})
                        st.toast("Producto añadido 🛒")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Próximamente nuevos productos.")
    except Exception as e:
        st.error(f"Error al cargar productos: {e}")

# ==========================================
# PERFIL: COMERCIANTE (INVENTARIO)
# ==========================================
elif perfil == "🏢 Panel Comerciante":
    st.header("🏢 Gestión de Inventario")
    
    with st.expander("➕ Cargar Producto a la Vitrina"):
        col1, col2 = st.columns(2)
        with col1:
            n_p = st.text_input("Nombre Producto")
            p_p = st.number_input("Precio ($)", min_value=0.0)
            c_p = st.text_input("Negocio / Comercio")
        with col2:
            s_p = st.number_input("Stock", min_value=0)
            u_p = st.text_input("Link de la Imagen")
            cat = st.selectbox("Categoría", ["Comida", "Ropa", "Salud", "Otros"])
            
        if st.button("PUBLICAR EN VITRINA"):
            supabase.table("productos").insert({
                "nombre_producto": n_p, "precio": p_p, "stock": s_p, 
                "imagen_url": u_p, "comercio_nombre": c_p, "categoria": cat
            }).execute()
            st.success("¡Producto publicado con éxito!")
            st.rerun()

    # Ver Inventario actual
    st.subheader("📋 Mi Inventario")
    res_inv = supabase.table("productos").select("*").execute()
    if res_inv.data:
        st.dataframe(pd.DataFrame(res_inv.data), use_container_width=True)

# ==========================================
# PERFIL: REPARTIDOR (ENTREGAS)
# ==========================================
else:
    st.header("🚚 Panel de Entregas")
    try:
        res_ped = supabase.table("pedidos").select("*").order("creado_el", desc=True).execute()
        pedidos = res_ped.data
        if pedidos:
            for ped in pedidos:
                with st.container():
                    st.markdown(f"""
                    ---
                    **ORDEN #{ped['id']}** | Cliente: {ped['cliente']}
                    - **Productos:** {ped['productos']}
                    - **DIRECCIÓN:** {ped['direccion']}
                    - **TOTAL A COBRAR:** {ped['total']} $
                    """)
                    if st.button(f"Marcar Entregado #{ped['id']}"):
                        supabase.table("pedidos").delete().eq("id", ped['id']).execute()
                        st.rerun()
        else:
            st.info("No hay entregas pendientes por ahora.")
    except:
        st.write("Esperando nuevos pedidos...")
