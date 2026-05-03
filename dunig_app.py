import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Configuración de Aplicación Multi-Usuario
st.set_page_config(page_title="D'UNIG Delivery Platinum", layout="wide")

# Conexión
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Estética Platinum
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #D4AF37; }
    .stButton>button { background-color: #D4AF37; color: black; border-radius: 8px; width: 100%; }
    .card { background-color: #1A1C23; padding: 20px; border-radius: 10px; border: 1px solid #D4AF37; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚜️ D'UNIG DELIVERY PLATINUM")

# --- SISTEMA DE NAVEGACIÓN ---
menu = st.tabs(["🏬 MI VITRINA (Comercios)", "🛒 COMPRAR (Clientes)", "🛵 ENTREGAS (Repartidores)"])

# 1. SECCIÓN COMERCIOS (Cargar Inventario)
with menu[0]:
    st.header("Gestión de Inventario")
    with st.expander("➕ Cargar Nuevo Producto a mi Vitrina"):
        comercio = st.text_input("Nombre de tu Comercio")
        p_nombre = st.text_input("Nombre del Producto")
        p_desc = st.text_area("Descripción/Detalles")
        p_precio = st.number_input("Precio ($)", min_value=0.0)
        p_stock = st.number_input("Stock Inicial", min_value=0)
        
        if st.button("SUBIR A LA VITRINA"):
            data = {"comercio_nombre": comercio, "producto_nombre": p_nombre, "descripcion": p_desc, "precio": p_precio, "stock": p_stock}
            supabase.table("productos").insert(data).execute()
            st.success("¡Producto publicado con éxito!")

# 2. SECCIÓN CLIENTES (Ver Vitrina y Comprar)
with menu[1]:
    st.header("Vitrina de Productos")
    productos_res = supabase.table("productos").select("*").execute()
    prod_df = pd.DataFrame(productos_res.data)

    if not prod_df.empty:
        for index, row in prod_df.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="card">
                    <h3>{row['producto_nombre']}</h3>
                    <p><b>Comercio:</b> {row['comercio_nombre']}</p>
                    <p>{row['descripcion']}</p>
                    <h4 style="color: #00FF00;">Precio: {row['precio']} $</h4>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"Añadir al Carrito: {row['producto_nombre']}", key=f"btn_{row['id']}"):
                    st.toast(f"Añadido: {row['producto_nombre']}")
                    # Aquí luego programaremos el carrito real
    else:
        st.info("Aún no hay productos en la vitrina.")

# 3. SECCIÓN REPARTIDORES
with menu[2]:
    st.header("Pedidos por Entregar")
    pedidos_res = supabase.table("pedidos").select("*").execute()
    pedidos_df = pd.DataFrame(pedidos_res.data)
    
    if not pedidos_df.empty:
        st.dataframe(pedidos_df)
    else:
        st.info("No hay pedidos pendientes por ahora.")
