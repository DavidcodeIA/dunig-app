import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import uuid

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
# Layout 'wide' para permitir que el video respire hacia los bordes
st.set_page_config(page_title="D'UNIG LUXURY", layout="wide", initial_sidebar_state="collapsed")

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
# 2. ESTÉTICA LUXURY + FULL WIDTH (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000000; color: #ffffff; }
    
    /* Botón Dorado Universal */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 15px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 55px !important; width: 100% !important;
    }

    /* Portadas Cuadradas Mall */
    .img-cuadrada {
        width: 100%; aspect-ratio: 1 / 1; object-fit: cover; 
        border-radius: 10px; border: 1px solid #333;
        margin-bottom: 10px; display: block;
    }

    /* VIDEO EXPANDIDO (TikTok Style) */
    .video-full {
        width: 100vw; position: relative; left: 50%; right: 50%;
        margin-left: -50vw; margin-right: -50vw;
        background: #000; line-height: 0;
    }
    video { width: 100% !important; height: auto !important; max-height: 80vh; object-fit: cover; }

    /* BARRA DE CONTROL INTEGRADA (Flecha + Info) */
    .control-bar {
        display: flex; align-items: center; gap: 10px;
        width: 100%; max-width: 500px; margin: -5px auto 10px auto;
    }

    /* Hack para Flecha Blanca Estilizada */
    div[data-testid="column"]:nth-child(1) button {
        background: transparent !important; border: 2px solid #ffffff !important;
        color: #ffffff !important; border-radius: 12px !important;
        width: 52px !important; height: 52px !important; font-size: 22px !important;
    }

    .info-luxury-box {
        flex-grow: 1; display: flex; justify-content: space-between; align-items: center;
        background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
        padding: 0 15px; height: 52px; border-radius: 12px; border: 1px solid rgba(212,175,55,0.4);
    }

    .p-title { color: #D4AF37; font-size: 0.9rem; font-weight: 700; text-transform: uppercase; }
    .p-price { color: #39FF14; font-size: 1.1rem; font-weight: 900; }

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
        w = st.text_input("WhatsApp (Ej: 58412...)")
        p = st.selectbox("Plan", ["GRATUITO", "BRONCE", "PLATA", "ORO"])
        img = st.file_uploader("Portada Cuadrada", type=['jpg', 'png'])
        if st.form_submit_button("REGISTRAR"):
            if n and e and w and img:
                path = f"portadas/{uuid.uuid4()}.jpg"
                supabase.storage.from_("fotos_productos").upload(path, img.getvalue())
                url = supabase.storage.from_("fotos_productos").get_public_url(path)
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": n, "email_propietario": e.lower(),
                    "whatsapp": w, "portada_url": url, "plan": p, "codigo_acceso": "LUXURY7"
                }).execute()
                st.success("¡Registrado! Ya puedes entrar al panel admin.")
                ir_a('mall')

elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL SOCIO</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        m = st.text_input("Email")
        c = st.text_input("Código", type="password")
        if st.button("🔓 ENTRAR"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m.lower()).execute()
            if res.data and str(res.data[0]['codigo_acceso']).upper() == c.upper():
                st.session_state.logged_in = True; st.session_state.user_email = m.lower(); st.session_state.user_data = res.data[0]; st.rerun()
    else:
        u = st.session_state.user_data
        st.write(f"Tienda: **{u['nombre_comercio']}** | Plan: **{u['plan']}**")
        
        with st.form("nuevo_p"):
            st.subheader("Subir Nuevo Producto")
            nom_p = st.text_input("Nombre Producto")
            pre_p = st.number_input("Precio ($)", min_value=0.0)
            vid_p = st.file_uploader("Video MP4", type=['mp4'])
            if st.form_submit_button("🚀 PUBLICAR"):
                if nom_p and vid_p:
                    v_path = f"videos/{u['nombre_comercio']}/{uuid.uuid4()}.mp4"
                    supabase.storage.from_("fotos_productos").upload(v_path, vid_p.getvalue())
                    v_url = supabase.storage.from_("fotos_productos").get_public_url(v_path)
                    supabase.table("productos").insert({
                        "nombre_producto": nom_p, "precio": pre_p,
                        "video_url": v_url, "comercio_relacionado": u['nombre_comercio']
                    }).execute()
                    st.success("¡Producto en vivo!")

elif st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    cols = st.columns(2)
    for i, t in enumerate(tiendas):
        with cols[i % 2]:
            st.markdown(f'<img src="{t["portada_url"]}" class="img-cuadrada">', unsafe_allow_html=True)
            if st.button(f"ENTRAR {t['nombre_comercio'].upper()}", key=f"t_{t['id']}"):
                st.session_state.tienda_actual = t
                ir_a('tienda')

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        # 1. VIDEO FULL WIDTH
        st.markdown('<div class="video-full">', unsafe_allow_html=True)
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 2. BARRA DE CONTROL (FLECHA AL LADO DEL NOMBRE/PRECIO)
        c1, c2 = st.columns([1, 5])
        with c1:
            if st.button("←", key=f"back_{p['id']}"):
                ir_a('mall')
        with c2:
            st.markdown(f"""
                <div class="info-luxury-box">
                    <span class="p-title">{p['nombre_producto']}</span>
                    <span class="p-price">${p['precio']}</span>
                </div>
            """, unsafe_allow_html=True)

        # 3. BOTÓN COMPRA
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            ventana_pago(p, t)
        
        st.divider()