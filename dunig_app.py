import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONEXIÓN Y CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="centered")

@st.cache_resource
def init_connection():
    # Asegúrate de tener estas variables en st.secrets
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS: INTERFAZ LUXURY & BURBUJA FLOTANTE
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; }
    
    /* Botón Atrás FIJO */
    .fixed-back {
        position: fixed;
        top: 20px;
        left: 20px;
        z-index: 1000;
    }

    /* Contenedor de Video con Relieve Dorado */
    .video-container {
        position: relative;
        width: 100%;
        border-radius: 30px;
        border: 3px solid #D4AF37;
        overflow: hidden;
        margin-bottom: 15px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.9);
        background-color: #000;
    }

    /* BURBUJA FLOTANTE DE PRECIO (ESTILO PLATINUM) */
    .price-bubble {
        position: absolute;
        top: 25px;
        right: 25px;
        background: linear-gradient(135deg, #FFD700 0%, #D4AF37 50%, #B8860B 100%);
        color: #000;
        padding: 12px 25px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.6rem;
        z-index: 99;
        border: 2px solid #FFFFFF;
        box-shadow: 0 8px 20px rgba(212, 175, 55, 0.6);
        font-family: 'Arial Black', sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Botones Estilo 3D Premium */
    .stButton>button {
        background: linear-gradient(145deg, #D4AF37, #B8860B) !important;
        color: white !important;
        border-radius: 20px !important;
        font-weight: 900 !important;
        border: 1px solid #FFD700 !important;
        box-shadow: 0 6px 0 #5d4814, 0 10px 20px rgba(0,0,0,0.5) !important;
        transition: all 0.15s ease;
        height: 55px !important;
    }
    
    .stButton>button:active {
        box-shadow: 0 2px 0 #5d4814 !important;
        transform: translateY(4px);
    }

    hr { border-top: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DE TICKET WHATSAPP
# ==========================================
@st.dialog("💎 FINALIZAR COMPRA")
def ventana_pago(producto, comercio):
    # Consulta de seguridad para obtener datos más recientes
    res = supabase.table("perfiles_comercio").select("datos_pago, whatsapp, nombre_comercio").eq("id", comercio['id']).single().execute()
    tienda = res.data
    
    st.markdown(f"### 🛍️ {producto['nombre_producto']}")
    st.markdown(f"**Total a transferir:** `${producto['precio']}`")
    st.divider()
    
    st.markdown("### 🏦 Cuentas de Pago")
    st.info(tienda.get('datos_pago', '⚠️ El vendedor aún no ha configurado sus datos.'))
    
    referencia = st.text_input("Ingresa el Número de Referencia", help="Número de confirmación de tu banco")
    
    if st.button("📲 ENVIAR TICKET Y VALIDAR", use_container_width=True):
        if referencia:
            msj = (
                f"✨ *ORDEN DE COMPRA D'UNIG PLATINUM*\n\n"
                f"📦 *Producto:* {producto['nombre_producto']}\n"
                f"💰 *Precio:* ${producto['precio']}\n"
                f"🔢 *Referencia:* {referencia}\n"
                f"🏪 *Tienda:* {tienda['nombre_comercio']}\n\n"
                f"🚀 _Enviado desde el sistema de ventas D'UNIG._"
            )
            
            link = f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}"
            
            # Registro de pedido
            supabase.table("pedidos").insert({
                "producto": producto['nombre_producto'],
                "precio": producto['precio'],
                "referencia": referencia,
                "comercio": tienda['nombre_comercio']
            }).execute()
            
            st.success("¡Ticket generado con éxito!")
            st.link_button("ABRIR MI WHATSAPP", link)
        else:
            st.warning("Debes colocar la referencia para que el dueño verifique tu pago.")

# ==========================================
# 4. NAVEGACIÓN Y VISTAS
# ==========================================

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg")
    st.markdown("---")
    if st.button("🏠 MALL", use_container_width=True): ir_a('mall')
    if st.button("⚙️ PANEL CONTROL", use_container_width=True): ir_a('admin')

# --- VISTA: MALL ---
if st.session_state.view == 'mall':
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg", use_container_width=True)
    st.markdown("<h2 style='text-align:center; color:#D4AF37;'>BIENVENIDO AL MALL PLATINUM</h2>", unsafe_allow_html=True)
    
    buscar = st.text_input("🔍 Buscar tiendas o productos...", placeholder="Escribe aquí...")
    
    t_data = supabase.table("perfiles_comercio").select("*").execute()
    for t in t_data.data:
        if buscar.lower() in t['nombre_comercio'].lower():
            if st.button(f"✨ ENTRAR A {t['nombre_comercio'].upper()}", key=f"t_{t['id']}", use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA: TIENDA ---
elif st.session_state.view == 'tienda':
    # BOTÓN ATRÁS FIJO (Z-INDEX ALTO)
    st.markdown('<div class="fixed-back">', unsafe_allow_html=True)
    if st.button("⬅️ VOLVER", key="btn_fijo"): ir_a('mall')
    st.markdown('</div>', unsafe_allow_html=True)
    
    t_act = st.session_state.tienda_actual
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t_act['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t_act['nombre_comercio']).execute()
    
    for p in prods.data:
        with st.container():
            # BURBUJA DE PRECIO DENTRO DEL CONTENEDOR DEL VIDEO
            st.markdown(f'''
                <div class="video-container">
                    <div class="price-bubble">${p['precio']}</div>
                </div>
            ''', unsafe_allow_html=True)
            st.video(p['video_url'])
            
            if st.button(f"🛒 COMPRAR YA: {p['nombre_producto']}", key=f"p_{p['id']}", use_container_width=True):
                ventana_pago(p, t_act)
            st.markdown("<br><br>", unsafe_allow_html=True)

# --- VISTA: ADMIN ---
elif st.session_state.view == 'admin':
    if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
    st.title("🚀 PANEL DE GESTIÓN")
    
    mail = st.text_input("Tu Correo de Propietario")
    if mail:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
        if res.data:
            perf = res.data[0]
            tb1, tb2, tb3 = st.tabs(["📤 SUBIR", "📦 STOCK", "💰 PAGOS"])
            
            with tb3:
                st.write("### Datos para tus Clientes")
                info_bancaria = st.text_area("Cuentas bancarias, Pago Móvil, etc.", value=perf.get('datos_pago', ''), height=150)
                if st.button("💾 GUARDAR DATOS DE PAGO"):
                    supabase.table("perfiles_comercio").update({"datos_pago": info_bancaria}).eq("id", perf['id']).execute()
                    st.success("¡Datos actualizados!")

            with tb1:
                with st.form("new_v", clear_on_submit=True):
                    name = st.text_input("Nombre del Producto")
                    price = st.number_input("Precio ($)", min_value=0.0)
                    file = st.file_uploader("Video Vertical", type=['mp4', 'mov'])
                    if st.form_submit_button("🚀 PUBLICAR"):
                        if file and name:
                            fname = f"vid_{random.randint(100,999)}_{file.name}"
                            path = f"videos/{perf['nombre_comercio']}/{fname}"
                            supabase.storage.from_("fotos_productos").upload(path, file.getvalue())
                            url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                            supabase.table("productos").insert({"nombre_producto": name, "precio": price, "video_url": url_v, "comercio_relacionado": perf['nombre_comercio']}).execute()
                            st.success("¡Producto en línea!")
                            st.rerun()

            with tb2:
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"**{i['nombre_producto']}** - ${i['precio']}")
                    if c2.button("🗑️", key=f"d_{i['id']}"):
                        supabase.table("productos").delete().eq("id", i['id']).execute()
                        st.rerun()
