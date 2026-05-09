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

PLANES = {
    "GRATUITO": 3,
    "BRONCE": 10,
    "PLATA": 25,
    "ORO": 9999
}

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
    
    /* Botones Dorados Luxury */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 30px !important;
        font-weight: 800 !important; text-transform: uppercase;
        border: none !important;
    }

    .img-redonda {
        width: 140px; height: 140px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 10px auto; display: block;
        box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.4);
    }

    /* Burbuja de Precio Flotante */
    .price-bubble {
        position: absolute; top: 20px; left: 20px;
        background: rgba(0, 0, 0, 0.8); color: #39FF14; 
        padding: 8px 18px; border-radius: 50px;
        font-weight: 900; border: 2px solid #39FF14; z-index: 99;
    }

    /* CONTENEDOR FORMATO TIKTOK (9:16) CON ZONAS SEGURAS */
    .video-container {
        position: relative;
        width: 100%;
        max-width: 450px; /* Tamaño máximo sugerido para desktop */
        aspect-ratio: 9 / 16;
        margin: auto;
        background: #000;
        border-radius: 15px;
        overflow: hidden;
        border: 2px solid #333;
    }

    /* Simulación de la interfaz de TikTok para visualizar zonas seguras */
    .tiktok-overlay {
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        pointer-events: none; /* No interfiere con clicks */
        z-index: 10;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Ajuste de márgenes según especificaciones 2026 */
    .safe-content-area {
        margin-top: 15%;    /* Margen superior (Nombre/Texto) */
        margin-bottom: 25%; /* Margen inferior (Descripción/Botones) */
        margin-right: 15%;  /* Margen lateral derecho (Acciones) */
        margin-left: 5%;
        height: 60%;
        border: 1px dashed rgba(255,255,255,0.1); /* Guía visual opcional */
    }

    video {
        width: 100% !important;
        height: 100% !important;
        object-fit: cover;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DEL CARRITO
# ==========================================
@st.dialog("💎 CARRITO D'UNIG LUXURY")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **DATOS DE PAGO:**\n{tienda.get('datos_pago', 'Consultar al vendedor')}")
    ref = st.text_input("Ingrese Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Producto:* {producto['nombre_producto']}\n🔢 *Cant:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").replace(" ", "").strip()
            st.link_button("ENVIAR POR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else: st.error("Por favor, ingrese la referencia de pago")

# ==========================================
# 4. LÓGICA DE VISTAS (MODIFICADA CON VIDEO TIKTOK)
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

if es_registro:
    # (El código de registro se mantiene igual...)
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE NUEVO SOCIO</h1>", unsafe_allow_html=True)
    with st.expander("💳 VER CUENTAS BANCARIAS PARA ACTIVACIÓN", expanded=True):
        st.markdown("""
        **Paga tu plan y pega la referencia abajo para activar tu tienda:**
        * **Pago Móvil:** Banco (0102) - CI: 12.345.678
        """)
    
    with st.form("form_reg_externo", clear_on_submit=True):
        rn = st.text_input("Nombre de la Tienda")
        rm = st.text_input("Email del Propietario")
        rt = st.text_input("WhatsApp (Ej: 58412...)")
        plan_sel = st.selectbox("Plan", ["GRATUITO", "BRONCE", "PLATA", "ORO"])
        ri = st.file_uploader("Foto de Portada", type=['jpg', 'png'])
        ref_socio = st.text_input("Referencia de Pago")

        if st.form_submit_button("REGISTRAR COMERCIO"):
            if rn and rm and rt and ri and ref_socio:
                path_i = f"portadas/reg_{random.randint(1000,9999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path_i, ri.getvalue())
                url_i = supabase.storage.from_("fotos_productos").get_public_url(path_i)
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": rn, "email_propietario": rm.lower(), 
                    "whatsapp": rt, "portada_url": url_i, "plan": plan_sel, "codigo_acceso": "LUXURY7"
                }).execute()
                st.success("¡Registro Exitoso!")
                ir_a('mall')

elif not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        res = supabase.table("perfiles_comercio").select("*").execute()
        tiendas = res.data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        url = t.get('portada_url') or "https://via.placeholder.com/150"
                        st.markdown(f'<img src="{url}" class="img-redonda">', unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; color:#D4AF37; font-weight:bold;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                        if st.button("VISITAR", key=f"m_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        st.button("⬅️ VOLVER AL MALL", on_click=lambda: ir_a('mall'))
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        
        for p in prods.data:
            # --- CONTENEDOR TIKTOK CON MEDIDAS 2026 ---
            st.markdown(f"""
                <div class="video-container">
                    <div class="price-bubble">${p['precio']}</div>
                    <div class="tiktok-overlay">
                        <div class="safe-content-area"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # El video se renderiza justo después del div para que Streamlit lo maneje
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            
            st.markdown(f"<h3 style='text-align:center;'>{p['nombre_producto']}</h3>", unsafe_allow_html=True)
            if st.button(f"🛒 ADQUIRIR AHORA", key=f"btn_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.divider()

else:
    # (El resto del Panel Admin se mantiene igual...)
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        m = st.text_input("Email")
        c = st.text_input("Código", type="password")
        if st.button("🔓 ENTRAR"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m.lower()).execute()
            if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == c.upper():
                st.session_state.logged_in = True; st.session_state.user_email = m; st.rerun()
    else:
        st.write(f"Bienvenido, {st.session_state.user_email}")
        if st.button("🚪 CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()