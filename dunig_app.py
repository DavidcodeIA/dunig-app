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
# 2. ESTÉTICA LUXURY + PORTADAS CUADRADAS
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 10px !important; /* Más cuadrado también */
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        margin-top: 5px !important;
    }

    /* PORTADAS CUADRADAS SIN MARCO */
    .img-cuadrada {
        width: 100%; 
        aspect-ratio: 1 / 1; 
        object-fit: cover; 
        border-radius: 0px; /* Elimina redondez */
        margin-bottom: 10px;
        display: block;
    }

    .video-wrapper {
        position: relative; width: 100%; max-width: 400px;
        margin: auto; background-color: #000;
        border-radius: 20px; border: 2px solid #333; overflow: hidden;
    }

    .product-info-block {
        display: flex; justify-content: center; align-items: center;
        gap: 12px; margin-top: 15px; margin-bottom: 5px;
    }

    .product-title { color: #D4AF37; font-size: 1.25rem; font-weight: 700; text-transform: uppercase; }
    
    .price-tag {
        background: #000; color: #39FF14; padding: 4px 12px;
        border-radius: 8px; font-weight: 900; border: 1px solid #39FF14;
    }

    video { width: 100% !important; height: 100% !important; object-fit: cover !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS Y LÓGICA
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

es_admin = st.query_params.get("admin") == "true"
es_reg = st.query_params.get("reg") == "true"

if es_reg:
    # Lógica de registro (se mantiene igual)
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO SOCIO</h1>", unsafe_allow_html=True)
    with st.form("reg_form"):
        n = st.text_input("Nombre Tienda")
        e = st.text_input("Email")
        w = st.text_input("WhatsApp")
        p = st.selectbox("Plan", ["GRATUITO", "BRONCE", "PLATA", "ORO"])
        img = st.file_uploader("Portada", type=['jpg', 'png'])
        ref_p = st.text_input("Ref. Pago Activación")
        if st.form_submit_button("REGISTRAR"):
            if n and e and w and img and ref_p:
                path = f"portadas/{random.randint(100,999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path, img.getvalue())
                url = supabase.storage.from_("fotos_productos").get_public_url(path)
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": n, "email_propietario": e.lower(),
                    "whatsapp": w, "portada_url": url, "plan": p, "codigo_acceso": "LUXURY7"
                }).execute()
                st.success("Registrado correctamente.")
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
                        # APLICACIÓN DE LA IMAGEN CUADRADA LIMPIA
                        st.markdown(f'<img src="{t["portada_url"]}" class="img-cuadrada">', unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; font-weight:700; font-size:1.1rem;'>{t['nombre_comercio']}</p>", unsafe_allow_html=True)
                        if st.button("VISITAR", key=f"t_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        st.button("⬅️ VOLVER AL MALL", on_click=lambda: ir_a('mall'))
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        for p in prods:
            st.markdown('<div class="video-wrapper">', unsafe_allow_html=True)
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="product-info-block"><span class="product-title">{p["nombre_producto"]}</span><span class="price-tag">${p["price"]}</span></div>', unsafe_allow_html=True)
            if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.divider()