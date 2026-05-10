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
# 2. ESTÉTICA LUXURY + ZONAS SEGURAS (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 30px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        margin-top: 5px !important;
    }

    .img-redonda {
        width: 140px; height: 140px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 10px auto; display: block;
        box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.4);
    }

    .video-wrapper {
        position: relative; width: 100%; max-width: 400px;
        margin: auto; background-color: #000;
        border-radius: 20px; border: 2px solid #333; overflow: hidden;
    }

    .tiktok-overlay {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; z-index: 5;
    }

    .safe-area-guide {
        margin-top: 15%; margin-bottom: 25%; margin-right: 15%; margin-left: 5%;
        height: 60%;
    }

    /* Contenedor de Información Inferior */
    .product-info-block {
        display: flex; justify-content: center; align-items: center;
        gap: 12px; margin-top: 15px; margin-bottom: 5px;
    }

    .product-title { color: #D4AF37; font-size: 1.25rem; font-weight: 700; text-transform: uppercase; }
    
    .price-tag {
        background: #000; color: #39FF14; padding: 4px 12px;
        border-radius: 8px; font-weight: 900; border: 1px solid #39FF14;
        box-shadow: 0px 0px 10px rgba(57, 255, 20, 0.2);
    }

    video { width: 100% !important; height: 100% !important; object-fit: cover !important; }
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
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO SOCIO</h1>", unsafe_allow_html=True)
    with st.form("reg_form"):
        n = st.text_input("Nombre Tienda")
        e = st.text_input("Email")
        w = st.text_input("WhatsApp (58...)")
        p = st.selectbox("Plan", ["GRATUITO", "BRONCE", "PLATA", "ORO"])
        img = st.file_uploader("Portada", type=['jpg', 'png'])
        ref = st.text_input("Ref. Pago Activación")
        if st.form_submit_button("REGISTRAR"):
            if n and e and w and img and ref:
                path = f"portadas/{random.randint(100,999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path, img.getvalue())
                url = supabase.storage.from_("fotos_productos").get_public_url(path)
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": n, "email_propietario": e.lower(),
                    "whatsapp": w, "portada_url": url, "plan": p, "codigo_acceso": "LUXURY7"
                }).execute()
                st.success("¡Éxito! Notifica al administrador.")
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
            # 1. Video Primero (Siguiendo formato TikTok)
            st.markdown('<div class="video-wrapper"><div class="tiktok-overlay"><div class="safe-area-guide"></div></div>', unsafe_allow_html=True)
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # 2. Nombre y Precio (Justo debajo del video y arriba del botón)
            st.markdown(f"""
                <div class="product-info-block">
                    <span class="product-title">{p['nombre_producto']}</span>
                    <span class="price-tag">${p['precio']}</span>
                </div>
            """, unsafe_allow_html=True)

            # 3. Botón de Compra
            if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.divider()

else:
    # --- PANEL ADMIN ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL CONTROL</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        m = st.text_input("Email")
        c = st.text_input("Código", type="password")
        if st.button("🔓 ENTRAR"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m.lower()).execute()
            if res.data and str(res.data[0]['codigo_acceso']).upper() == c.upper():
                st.session_state.logged_in = True; st.session_state.user_email = m.lower(); st.rerun()
    else:
        # El resto del panel admin se mantiene igual...
        st.write(f"Conectado como: **{st.session_state.user_email}**")
        if st.button("🚪 CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()