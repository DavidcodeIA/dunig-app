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

# --- FUNCIONES DE APOYO (Ponlas al principio del código) ---
def añadir_al_carrito(nombre, precio):
    st.session_state.carrito.append({'nombre': nombre, 'precio': precio})
    st.toast(f"✨ {nombre} añadido")

def ir_al_pago():
    st.session_state.checkout = True

# ==========================================
# PERFIL: CLIENTE (VELOCIDAD Y DORADO LUXURY)
# ==========================================
if perfil == "🛒 Vitrina Cliente":
    
    # --- PANTALLA DE PAGO (CHECKOUT) ---
    if st.session_state.get('checkout', False):
        st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🏦 PROCESAR PAGO</h1>", unsafe_allow_html=True)
        
        total_pagar = sum(item['precio'] for item in st.session_state.carrito)
        
        col_check1, col_check2 = st.columns([2, 1])
        
        with col_check1:
            st.markdown(f"""
            <div style='background-color: #1A1C23; padding: 20px; border-radius: 15px; border-left: 5px solid #D4AF37;'>
                <h3 style='color: #D4AF37;'>Resumen de Orden</h3>
                {''.join([f"<p style='margin:0;'>🔸 {i['nombre']} - <b>{i['precio']}$</b></p>" for i in st.session_state.carrito])}
                <hr>
                <h2 style='color: #D4AF37;'>Total: {total_pagar}$</h2>
            </div>
            """, unsafe_allow_html=True)

        with col_check2:
            st.info("💳 **PAGO MÓVIL**\n\nBVC (0102)\n0412-5555555\nV-12.345.678")

        st.write("---")
        st.subheader("🚚 Datos de Entrega")
        
        nombre_c = st.text_input("👤 Tu Nombre")
        
        # --- BOTÓN DE UBICACIÓN AUTOMÁTICA ---
        st.markdown("👇 *Presiona para capturar tu ubicación actual*")
        if st.button("📍 OBTENER MI UBICACIÓN ACTUAL"):
            # Nota: La geolocalización real requiere un componente llamado 'streamlit-js-eval'
            # Por ahora, simulamos la captura para no romper tu flujo actual
            st.session_state.direccion_automatica = "Ubicación GPS capturada (Cerca de tu zona)"
        
        direccion_final = st.text_input("📍 Confirmar Dirección Exacta", 
                                        value=st.session_state.get('direccion_automatica', ""))

        c_p1, c_p2 = st.columns(2)
        if c_p1.button("🔥 CONFIRMAR PEDIDO (INSTANTÁNEO)"):
            if nombre_c and direccion_final:
                # Lógica de inserción...
                supabase.table("pedidos").insert({
                    "cliente": nombre_c, "productos": str(st.session_state.carrito),
                    "total": total_pagar, "direccion": direccion_final
                }).execute()
                st.balloons()
                st.success("✅ ¡ORDEN RECIBIDA! Dios bendiga tu compra.")
                st.session_state.carrito = []
                st.session_state.checkout = False
                st.rerun()
        
        if c_p2.button("⬅️ SEGUIR COMPRANDO"):
            st.session_state.checkout = False
            st.rerun()

    # --- PANTALLA DE VITRINA ---
    else:
        st.markdown("<h1 style='text-align: center; color: #D4AF37;'>⚜️ VITRINA D'UNIG ⚜️</h1>", unsafe_allow_html=True)
        
        # Carrito flotante instantáneo
        if st.session_state.carrito:
            t = sum(i['precio'] for i in st.session_state.carrito)
            st.button(f"🛒 PAGAR AHORA ({t}$)", on_click=ir_al_pago)

        try:
            res = supabase.table("productos").select("*").execute()
            productos = res.data
            if productos:
                cols = st.columns(2)
                for i, p in enumerate(productos):
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div style='border: 1px solid #D4AF37; padding: 10px; border-radius: 15px; background: #1A1C23;'>
                            <img src='{p['imagen_url'] if p['imagen_url'] else 'https://via.placeholder.com/150'}' style='width:100%; border-radius: 10px;'>
                            <h4 style='color: #D4AF37; margin-top: 10px;'>{p['nombre_producto']}</h4>
                            <p style='font-size: 20px; font-weight: bold;'>{p['precio']}$</p>
                        </div>
                        """, unsafe_allow_html=True)
                        # El secreto del clic único: usar on_click
                        st.button(f"Añadir ➕", key=f"btn_{p['id']}_{i}", 
                                  on_click=añadir_al_carrito, args=(p['nombre_producto'], p['precio']))
            else:
                st.info("Esperando nuevos tesoros en la vitrina...")
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
