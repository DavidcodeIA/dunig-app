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
# 2. CSS: ESTÉTICA ULTRA-MODERNA
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    
    /* Animación de carga rápida */
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    .loading-text { font-weight: bold; color: #D4AF37; animation: pulse 1.5s infinite; }

    .fixed-back { position: fixed; top: 15px; left: 15px; z-index: 3000; }

    .video-container {
        width: 100%;
        border-radius: 25px;
        border: 2px solid #D4AF37;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.3);
        margin-bottom: 15px;
    }

    .price-bubble {
        position: absolute;
        top: 15px;
        right: 15px;
        background: rgba(0,0,0,0.7);
        backdrop-filter: blur(10px);
        color: #FFD700;
        padding: 5px 18px;
        border-radius: 30px;
        font-weight: 800;
        border: 1px solid #D4AF37;
        z-index: 1000;
    }

    /* Botones Estilo Cristal */
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #8A6E2F 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        letter-spacing: 1px;
        transition: 0.3s all !important;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. COMPONENTES DINÁMICOS
# ==========================================

@st.dialog("💎 PROCESAR COMPRA")
def ventana_pago(producto, comercio_id):
    res = supabase.table("perfiles_comercio").select("*").eq("id", comercio_id).single().execute()
    tienda = res.data
    
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    st.markdown(f"**Total a transferir:** `${producto['precio']}`")
    
    # Mostrar Datos de Pago (Texto o Imagen)
    info_pago = tienda.get('datos_pago')
    if info_pago:
        if "http" in info_pago:
            st.image(info_pago, caption="Escanea o usa estos datos")
        else:
            st.info(info_pago)
    
    ref = st.text_input("Referencia de la operación")
    
    if st.button("🚀 FINALIZAR POR WHATSAPP", use_container_width=True):
        if ref:
            msj = f"✨ *PEDIDO PLATINUM*\n📦 *{producto['nombre_producto']}*\n💰 *${producto['precio']}*\n🔢 *Ref:* {ref}"
            url_wa = f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}"
            st.link_button("ABRIR WHATSAPP", url_wa)
        else: st.warning("Ingresa la referencia.")

# ==========================================
# 4. VISTAS
# ==========================================

with st.sidebar:
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg")
    st.button("🏠 EXPLORAR MALL", on_click=ir_a, args=('mall',), use_container_width=True)
    st.button("⚙️ ADMINISTRAR", on_click=ir_a, args=('admin',), use_container_width=True)

# --- TIENDA ---
if st.session_state.view == 'tienda':
    st.markdown('<div class="fixed-back">', unsafe_allow_html=True)
    if st.button("⬅️"): ir_a('mall')
    st.markdown('</div>', unsafe_allow_html=True)
    
    t = st.session_state.tienda_actual
    st.markdown(f"<h2 style='text-align:center;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    
    for p in prods.data:
        with st.container():
            st.markdown(f'<div class="product-card"><div class="price-bubble">${p["precio"]}</div><div class="video-container">', unsafe_allow_html=True)
            st.video(p['video_url'])
            st.markdown('</div></div>', unsafe_allow_html=True)
            if st.button(f"🛒 COMPRAR: {p['nombre_producto']}", key=f"p_{p['id']}", use_container_width=True):
                ventana_pago(p, t['id'])

# --- MALL ---
elif st.session_state.view == 'mall':
    st.title("🏙️ PLATINUM MALL")
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    cols = st.columns(2)
    for idx, t in enumerate(tiendas.data):
        with cols[idx % 2]:
            if st.button(f"✨ {t['nombre_comercio']}", key=t['id'], use_container_width=True):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- PANEL ADMIN: VELOCIDAD PURA ---
elif st.session_state.view == 'admin':
    st.title("🚀 FAST ADMIN")
    mail = st.text_input("Correo Propietario")
    
    if mail:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
        if res.data:
            perf = res.data[0]
            t1, t2 = st.tabs(["⚡ CARGA INSTANTÁNEA", "📦 STOCK"])
            
            with t1:
                st.subheader("Subir Producto y Datos de Pago")
                
                # CASILLA DE CÁMARA PARA DATOS DE PAGO
                st.write("📸 **Foto de tus datos de Pago (Cámara o Galería)**")
                cam_pago = st.camera_input("Capturar datos de pago", key="cam_pago")
                
                with st.form("quick_load", clear_on_submit=True):
                    col_a, col_b = st.columns(2)
                    nom = col_a.text_input("Nombre")
                    pre = col_b.number_input("Precio", min_value=0.0)
                    
                    st.write("🎬 **Video del Producto**")
                    vid = st.file_uploader("Subir clip", type=['mp4', 'mov'])
                    
                    if st.form_submit_button("🚀 PUBLICAR TODO AHORA"):
                        # 1. Procesar Imagen de Pago si existe
                        if cam_pago:
                            p_path = f"pagos/{perf['id']}_pago.jpg"
                            supabase.storage.from_("fotos_productos").upload(p_path, cam_pago.getvalue(), {"upsert": "true"})
                            p_url = supabase.storage.from_("fotos_productos").get_public_url(p_path)
                            supabase.table("perfiles_comercio").update({"datos_pago": p_url}).eq("id", perf['id']).execute()
                        
                        # 2. Procesar Video y Producto
                        if vid and nom:
                            v_path = f"videos/{perf['id']}_{random.randint(1000,9999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(v_path, vid.getvalue())
                            v_url = supabase.storage.from_("fotos_productos").get_public_url(v_path)
                            
                            supabase.table("productos").insert({
                                "nombre_producto": nom, "precio": pre, 
                                "video_url": v_url, "comercio_relacionado": perf['nombre_comercio']
                            }).execute()
                            st.balloons()
                            st.success("¡Publicado en tiempo récord!")
                            st.rerun()

            with t2:
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    c1, c2 = st.columns([5, 1])
                    c1.write(f"**{i['nombre_producto']}** - ${i['precio']}")
                    if c2.button("🗑️", key=f"d_{i['id']}"):
                        supabase.table("productos").delete().eq("id", i['id']).execute()
                        st.rerun()
