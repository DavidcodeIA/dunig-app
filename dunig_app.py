import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

PLANES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY + VIDEO OVERLAY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 30px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        margin-top: 10px !important;
    }

    .video-wrapper {
        position: relative; width: 100%; max-width: 400px;
        margin: auto; background-color: #000;
        border-radius: 20px; border: 2px solid #333; overflow: hidden;
    }

    /* CAPA DE INFORMACIÓN SOBRE EL VIDEO */
    .video-info-overlay {
        position: absolute;
        bottom: 0; left: 0; width: 100%;
        padding: 60px 15px 25px 15px; /* Padding superior alto para el degradado */
        background: linear-gradient(transparent, rgba(0,0,0,0.8));
        z-index: 10;
        pointer-events: none;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }

    .shop-name-tag {
        color: #ffffff; font-size: 0.9rem; font-weight: 600;
        opacity: 0.9; text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
    }

    .product-title-tag {
        color: #D4AF37; font-size: 1.2rem; font-weight: 800;
        text-transform: uppercase; text-shadow: 1px 1px 4px rgba(0,0,0,0.6);
    }

    .price-badge {
        width: fit-content;
        background: #39FF14; color: #000;
        padding: 2px 10px; border-radius: 5px;
        font-weight: 900; font-size: 0.9rem;
        margin-top: 5px;
    }

    video { width: 100% !important; height: 100% !important; object-fit: cover !important; }
    
    .img-redonda {
        width: 120px; height: 120px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 10px auto; display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS
# ==========================================
@st.dialog("💎 CARRITO D'UNIG LUXURY")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.info(f"💳 **DATOS DE PAGO:**\n{tienda.get('datos_pago', 'Consultar al vendedor')}")
    ref = st.text_input("Ingrese Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Producto:* {producto['nombre_producto']}\n🔢 *Cant:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").replace(" ", "").strip()
            st.link_button("ENVIAR POR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else: st.error("Referencia requerida")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_reg = st.query_params.get("reg") == "true"

if es_reg:
    # (Misma lógica de registro...)
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO SOCIO</h1>", unsafe_allow_html=True)
    with st.form("reg_form"):
        n = st.text_input("Nombre Tienda")
        e = st.text_input("Email")
        w = st.text_input("WhatsApp")
        p = st.selectbox("Plan", ["GRATUITO", "BRONCE", "PLATA", "ORO"])
        img = st.file_uploader("Portada", type=['jpg', 'png'])
        ref_p = st.text_input("Ref. Pago")
        if st.form_submit_button("REGISTRAR"):
            if n and e and w and img:
                path = f"portadas/{random.randint(100,999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path, img.getvalue())
                url = supabase.storage.from_("fotos_productos").get_public_url(path)
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": n, "email_propietario": e.lower(),
                    "whatsapp": w, "portada_url": url, "plan": p, "codigo_acceso": "LUXURY7"
                }).execute()
                st.success("Registrado.")
                ir_a('mall')

elif not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        tiendas = supabase.table("perfiles_comercio").select("*").execute().data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i+j]
                    with cols[j]:
                        st.markdown(f'<img src="{t["portada_url"]}" class="img-redonda">', unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; font-weight:bold;'>{t['nombre_comercio']}</p>", unsafe_allow_html=True)
                        if st.button("VISITAR", key=f"t_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        st.button("⬅️ VOLVER AL MALL", on_click=lambda: ir_a('mall'))
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        for p in prods:
            # --- VIDEO CON INFO INTEGRADA (ESTILO TIKTOK) ---
            st.markdown(f'''
                <div class="video-wrapper">
                    <div class="video-info-overlay">
                        <div class="shop-name-tag">@{t['nombre_comercio'].replace(" ", "").lower()}</div>
                        <div class="product-title-tag">{p['nombre_producto']}</div>
                        <div class="price-badge">${p['precio']}</div>
                    </div>
            ''', unsafe_allow_html=True)
            
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Botón de Compra justo debajo del video
            if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.divider()

else:
    # (Panel Admin...)
    st.title("⚙️ PANEL ADMIN")
    if st.button("CERRAR SESIÓN"):
        st.session_state.logged_in = False
        st.rerun()