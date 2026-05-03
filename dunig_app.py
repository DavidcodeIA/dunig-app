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
# PERFIL: CLIENTE (FLUJO DE PAGO PROFESIONAL)
# ==========================================
if perfil == "🛒 Vitrina Cliente":
    
    # --- PASO 2: PANTALLA DE PAGO (CHECKOUT) ---
    if 'checkout' in st.session_state and st.session_state.checkout:
        st.title("🏦 Finalizar Pago")
        st.markdown("### Resumen de tu pedido")
        
        total_pagar = 0
        resumen_texto = ""
        for item in st.session_state.carrito:
            st.write(f"✅ {item['nombre']} - **{item['precio']}$**")
            total_pagar += item['precio']
            resumen_texto += f"{item['nombre']} ({item['precio']}$), "
        
        st.markdown(f"<h2 style='color: #D4AF37;'>TOTAL A PAGAR: {total_pagar} $</h2>", unsafe_allow_html=True)
        st.write("---")
        
        # --- DATOS DE PAGO DEL DUEÑO ---
        st.info("💎 **DATOS PARA TRANSFERENCIA:**\n\n"
                "• **Pago Móvil:** Banco Central - 0412-1234567 - V-12345678\n"
                "• **Zelle:** pagos@dunigplatinum.com\n"
                "• **Referencia:** Indica tu nombre al pagar.")
        
        st.subheader("🚚 Datos para el Repartidor")
        nombre_c = st.text_input("👤 Tu Nombre")
        direccion_c = st.text_input("📍 Dirección Exacta")
        
        col_pay1, col_pay2 = st.columns(2)
        if col_pay1.button("🚀 CONFIRMAR Y ENVIAR PEDIDO"):
            if nombre_c and direccion_c:
                data_pedido = {
                    "cliente": nombre_c,
                    "productos": resumen_texto,
                    "total": total_pagar,
                    "direccion": direccion_c
                }
                supabase.table("pedidos").insert(data_pedido).execute()
                st.balloons()
                st.success("¡GLORIA A DIOS! Pedido enviado. El repartidor verificará tu pago.")
                st.session_state.carrito = []
                st.session_state.checkout = False
                if st.button("Volver al inicio"): st.rerun()
            else:
                st.warning("Por favor rellena tus datos de entrega.")
        
        if col_pay2.button("⬅️ Volver a la Vitrina"):
            st.session_state.checkout = False
            st.rerun()

    # --- PASO 1: VITRINA DE PRODUCTOS ---
    else:
        st.title("🛍️ D'UNIG SHOPPING")
        
        # Botón flotante de Carrito (solo aparece si hay algo)
        if st.session_state.carrito:
            total_actual = sum(item['precio'] for item in st.session_state.carrito)
            if st.button(f"🛒 IR A PAGAR ({total_actual} $)"):
                st.session_state.checkout = True
                st.rerun()

        try:
            res = supabase.table("productos").select("*").execute()
            productos = res.data
            if productos:
                cols = st.columns(2)
                for i, p in enumerate(productos):
                    with cols[i % 2]:
                        st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
                        if p['imagen_url']:
                            st.image(p['imagen_url'], use_container_width=True)
                        st.write(f"**{p['nombre_producto']}**")
                        st.write(f"💰 {p['precio']} $")
                        # SOLUCIÓN AL ERROR DE KEY: usamos ID + índice para que sea único
                        if st.button(f"➕ Añadir", key=f"btn_{p['id']}_{i}"):
                            st.session_state.carrito.append({'nombre': p['nombre_producto'], 'precio': p['precio']})
                            st.toast(f"{p['nombre_producto']} al carrito")
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("La vitrina está siendo surtida. ¡Vuelve pronto!")
        except Exception as e:
            st.error(f"Error: {e}")
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
