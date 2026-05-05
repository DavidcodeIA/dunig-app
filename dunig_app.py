import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="centered")

# Conexión Segura
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("⚠️ Configura las credenciales de Supabase en Secrets.")
    st.stop()

# Manejo de navegación
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTILOS TIKTOK LUXURY
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; }
    
    /* Contenedor del video vertical */
    .video-card {
        border: 2px solid #D4AF37;
        border-radius: 20px;
        padding: 5px;
        margin-bottom: 30px;
        background: #111;
        position: relative;
    }
    
    /* Precio flotante sobre el video */
    .floating-price {
        position: absolute;
        top: 20px;
        right: 20px;
        background: rgba(212, 175, 55, 0.9);
        color: black;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.2rem;
        z-index: 10;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }

    .stButton>button {
        background: linear-gradient(90deg, #D4AF37, #8B6B1E) !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. COMPONENTES ESPECIALES
# ==========================================

@st.dialog("💎 PROCESAR PAGO")
def ventana_pago(producto, comercio):
    st.markdown(f"### Compra en: {comercio['nombre_comercio']}")
    st.write(f"**Producto:** {producto['nombre_producto']}")
    st.write(f"**Monto a transferir:** ${producto['precio']}")
    st.divider()
    
    st.markdown("### 🏦 Datos de Pago")
    st.info(comercio.get('datos_pago', "Contactar al dueño para datos de transferencia."))
    
    ref = st.text_input("Ingrese el número de referencia bancaria")
    
    if st.button("ENVIAR COMPROBANTE"):
        if ref:
            pedido_data = {
                "producto": producto['nombre_producto'],
                "precio": producto['precio'],
                "referencia": ref,
                "comercio": comercio['nombre_comercio'],
                "estado": "Pendiente"
            }
            # Guardamos en la tabla de pedidos
            supabase.table("pedidos").insert(pedido_data).execute()
            st.success("✅ ¡Referencia enviada! El dueño verificará el pago.")
            if st.button("Cerrar"): st.rerun()
        else:
            st.error("Debes ingresar la referencia.")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================

# --- VISTA 1: MALL (CENTRO COMERCIAL) ---
if st.session_state.view == 'mall':
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg", width=250)
    st.title("⚜️ D'UNIG PLATINUM")
    
    col_a, col_b = st.columns(2)
    with col_b:
        if st.button("🏢 Acceso Propietario"): ir_a('admin')

    st.markdown("---")
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    
    for t in tiendas.data:
        with st.container():
            st.markdown(f"### 🏬 {t['nombre_comercio']}")
            if st.button(f"Entrar a Ver Catálogo", key=t['id'], use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')
            st.markdown("<br>", unsafe_allow_html=True)

# --- VISTA 2: TIENDA (ESTILO TIKTOK) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    
    if not prods.data:
        st.info("Próximamente más videos...")
    
    for p in prods.data:
        with st.container():
            # Contenedor visual del Video
            st.markdown(f'<div class="video-card"><div class="floating-price">${p["precio"]}</div>', unsafe_allow_html=True)
            st.video(p['video_url'])
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Detalles y Botón de Compra
            st.subheader(p['nombre_producto'])
            if st.button(f"🛍️ COMPRAR {p['nombre_producto']}", key=f"buy_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.markdown("<br><hr>", unsafe_allow_html=True)
    
    if st.button("🔙 Volver al Centro Comercial"): ir_a('mall')

# --- VISTA 3: ADMIN (CARGA DE VIDEOS) ---
elif st.session_state.view == 'admin':
    st.title("🚀 Panel de Carga")
    email_check = st.text_input("Ingrese su correo de propietario")
    
    # Verificamos si el comercio existe
    perfil = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_check).execute()
    
    if perfil.data:
        comercio = perfil.data[0]
        st.success(f"Bienvenido, {comercio['nombre_comercio']}")
        
        with st.form("upload_form", clear_on_submit=True):
            nombre_p = st.text_input("Nombre del Producto")
            precio_p = st.number_input("Precio ($)", min_value=0.0)
            archivo_video = st.file_uploader("📸 Graba o sube tu video vertical", type=['mp4', 'mov'])
            
            if st.form_submit_button("PUBLICAR"):
                if archivo_video and nombre_p:
                    # Subir a Storage
                    file_path = f"videos/{comercio['nombre_comercio']}/{random.randint(1000,9999)}.mp4"
                    supabase.storage.from_("fotos_productos").upload(file_path, archivo_video.getvalue())
                    video_url = supabase.storage.from_("fotos_productos").get_public_url(file_path)
                    
                    # Guardar en DB
                    nuevo_prod = {
                        "nombre_producto": nombre_p,
                        "precio": precio_p,
                        "video_url": video_url,
                        "comercio_relacionado": comercio['nombre_comercio']
                    }
                    supabase.table("productos").insert(nuevo_prod).execute()
                    st.balloons()
                    st.success("¡Video publicado con éxito!")
                else:
                    st.warning("Completa todos los campos.")
    
    if st.button("🔙 Volver"): ir_a('mall')
