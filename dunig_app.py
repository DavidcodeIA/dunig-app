import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONEXIÓN Y CONFIGURACIÓN DE ALTO RENDIMIENTO
# ==========================================
st.set_page_config(
    page_title="D'UNIG PLATINUM", 
    layout="centered",
    initial_sidebar_state="collapsed" # Mantenemos el menú cerrado para mayor limpieza
)

@st.cache_resource
def init_connection():
    # Cacheamos la conexión para que la app sea mucho más rápida al navegar
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Diccionario de Planes para escalabilidad
PLANES = {
    "BRONCE": 5,
    "PLATINUM": 15,
    "DIAMANTE": 50
}

# --- DETECCIÓN DE ENLACE (Shopping vs Admin) ---
# Si el link tiene '?admin=true', muestra el panel de control. Si no, el Shopping.
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS: ESTÉTICA LUXURY REFINADA
# ==========================================
st.markdown("""
    <style>
    /* Fondo Negro Puro y Tipografía Blanca */
    .main { background-color: #000000; color: #ffffff; }
    
    /* Estética de los Botones Dorados */
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #8A6E2F 100%) !important;
        color: white !important;
        border-radius: 25px !important;
        border: none !important;
        font-weight: bold;
        transition: 0.3s;
        height: 45px;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.4);
    }

    /* Burbuja de Precio Neón */
    .price-bubble {
        position: absolute;
        top: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.85);
        color: #39FF14; 
        padding: 8px 22px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.4rem;
        border: 2px solid #39FF14;
        box-shadow: 0 0 15px rgba(57, 255, 20, 0.4);
        z-index: 100;
    }

    /* Ocultar elementos innecesarios de Streamlit para marca blanca */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VENTANA DE COMPRA (CARRITO)
# ==========================================
@st.dialog("💎 MI CARRITO D'UNIG")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    
    col_cant, col_total = st.columns([1, 1])
    cantidad = col_cant.number_input("Cantidad", min_value=1, value=1, step=1)
    total_pagar = float(producto['precio']) * cantidad
    col_total.metric("TOTAL A PAGAR", f"${total_pagar:,.2f}")
    
    st.divider()
    st.markdown("#### 💳 DATOS DE PAGO")
    datos_pago = tienda.get('datos_pago', 'No configurado')
    st.info(f"Paga a través de:\n\n**{datos_pago}**")

    ref = st.text_input("Número de Referencia de Pago", placeholder="Ingresa los dígitos aquí")
    
    if st.button("📲 FINALIZAR PEDIDO", use_container_width=True):
        if ref:
            msj = (
                f"✨ *NUEVO PEDIDO D'UNIG*\n"
                f"🏪 *Comercio:* {tienda['nombre_comercio']}\n"
                f"--------------------------\n"
                f"📦 *Producto:* {producto['nombre_producto']}\n"
                f"🔢 *Cant:* {cantidad} | *Total:* ${total_pagar:,.2f}\n"
                f"🎫 *Ref:* {ref}\n"
                f"--------------------------"
            )
            url_wa = f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}"
            st.link_button("🚀 ENVIAR A WHATSAPP", url_wa)
        else:
            st.error("Es necesaria la referencia para procesar el pedido.")

# ==========================================
# 4. LÓGICA DE PANELES DIVIDIDOS
# ==========================================

# ------------------------------------------
# PANEL 1: D'UNIG SHOPPING (Vista Clientes)
# ------------------------------------------
if not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG SHOPPING</h1>", unsafe_allow_html=True)
        tiendas = supabase.table("perfiles_comercio").select("*").execute()
        
        cols = st.columns(2)
        for idx, t in enumerate(tiendas.data):
            with cols[idx % 2]:
                st.markdown(f"<div style='border:1px solid #D4AF37; padding:10px; border-radius:15px; text-align:center; margin-bottom:10px;'>", unsafe_allow_html=True)
                if st.button(f"✨ {t['nombre_comercio'].upper()}", key=f"ml_{t['id']}"):
                    st.session_state.tienda_actual = t
                    ir_a('tienda')
                st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
        
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        
        for p in prods.data:
            st.markdown(f'<div style="position: relative;"><div class="price-bubble">${p["precio"]}</div></div>', unsafe_allow_html=True)
            st.video(p['video_url'])
            if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"sh_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.divider()

# ------------------------------------------
# PANEL 2: PANEL DE CONTROL (Vista Propietarios)
# ------------------------------------------
else:
    st.markdown("<h1 style='color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    mail = st.text_input("Correo de Propietario para Gestionar")
    
    if mail:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
        if res.data:
            perf = res.data[0]
            plan_usuario = perf.get('plan', 'BRONCE').upper()
            limite_actual = PLANES.get(plan_usuario, 5)
            
            # Estadísticas y Plan
            st.success(f"Sesión Activa: {perf['nombre_comercio']}")
            res_c = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            total_p = res_c.count if res_c.count else 0
            
            col1, col2 = st.columns(2)
            col1.metric("PLAN", plan_usuario)
            col2.metric("PRODUCTOS", f"{total_p} / {limite_actual}")
            st.progress(min(total_p / limite_actual, 1.0))
            
            t_add, t_inv, t_config = st.tabs(["➕ AGREGAR", "📦 INVENTARIO", "💳 PAGOS"])

            with t_config:
                nuevo_pago = st.text_area("Tus Datos de Pago (Banco, Pago Móvil, etc.)", value=str(perf.get('datos_pago', '')))
                if st.button("💾 GUARDAR CONFIGURACIÓN"):
                    supabase.table("perfiles_comercio").update({"datos_pago": nuevo_pago}).eq("id", perf['id']).execute()
                    st.success("Configuración actualizada.")

            with t_add:
                if total_p >= limite_actual:
                    st.error("Has llegado al límite de tu plan.")
                else:
                    with st.form("new_p", clear_on_submit=True):
                        n = st.text_input("Nombre del Producto")
                        p = st.number_input("Precio ($)", min_value=0.0)
                        v = st.file_uploader("Video publicitario", type=['mp4'])
                        if st.form_submit_button("🚀 PUBLICAR EN EL MALL"):
                            if n and v:
                                v_path = f"videos/{perf['id']}_{random.randint(1000,9999)}.mp4"
                                supabase.storage.from_("fotos_productos").upload(v_path, v.getvalue())
                                v_url = supabase.storage.from_("fotos_productos").get_public_url(v_path)
                                supabase.table("productos").insert({
                                    "nombre_producto": n, "precio": p, "video_url": v_url, 
                                    "comercio_relacionado": perf['nombre_comercio']
                                }).execute()
                                st.rerun()

            with t_inv:
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    with st.expander(f"📝 {i['nombre_producto']} - ${i['precio']}"):
                        if st.button("🗑️ ELIMINAR", key=f"d_{i['id']}"):
                            supabase.table("productos").delete().eq("id", i['id']).execute()
                            st.rerun()
        else:
            st.error("No se encontró ningún comercio asociado a este correo.")
