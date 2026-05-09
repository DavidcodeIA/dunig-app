import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="wide", initial_sidebar_state="collapsed")

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
# 2. ESTÉTICA LUXURY PRO (CSS INTEGRADO)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    
    /* Botones Premium con efecto dorado */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; text-transform: uppercase;
        border: none !important; transition: 0.3s;
        margin-top: 10px;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0px 0px 20px #D4AF37; }

    /* Portadas Cuadradas Full para el Mall */
    .img-portada-full {
        width: 100%; aspect-ratio: 1 / 1; object-fit: cover;
        border: 1px solid rgba(212, 175, 55, 0.4);
        border-radius: 15px; margin-bottom: 10px;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.5);
    }

    /* Vitrina de Productos Vertical (Efecto TikTok) */
    .product-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(212, 175, 55, 0.15);
        border-radius: 25px;
        padding: 20px;
        margin-bottom: 30px;
        backdrop-filter: blur(15px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.7);
        text-align: center;
    }

    .price-badge {
        background: linear-gradient(135deg, #D4AF37, #F9F295);
        color: #000;
        padding: 5px 15px;
        border-radius: 10px;
        font-weight: 900;
        font-size: 1.3rem;
        display: inline-block;
        margin-bottom: 15px;
    }

    /* OPTIMIZACIÓN 9:16 PARA VIDEOS VERTICALES */
    .stVideo { 
        aspect-ratio: 9 / 16 !important; 
        width: 100%; 
        border-radius: 20px; 
        overflow: hidden; 
        border: 1px solid rgba(212, 175, 55, 0.3);
    }
    .stVideo video { object-fit: cover !important; }

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
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE NUEVO SOCIO</h1>", unsafe_allow_html=True)
    with st.form("form_reg_externo", clear_on_submit=True):
        rn = st.text_input("Nombre de la Tienda")
        rm = st.text_input("Email del Propietario")
        rt = st.text_input("WhatsApp (Ej: 58412...)")
        opciones_plan = {"GRATUITO": "🎁 GRATUITO ($0)", "BRONCE": "🥉 BRONCE ($5)", "PLATA": "🥈 PLATA ($15)", "ORO": "🥇 ORO ($30)"}
        plan_label = st.selectbox("Plan", options=list(opciones_plan.values()))
        plan_sel = [k for k, v in opciones_plan.items() if v == plan_label][0]
        ri = st.file_uploader("Foto de Portada (Cuadrada recomendada)", type=['jpg', 'png'])
        ref_socio = st.text_input("Referencia de Pago")

        if st.form_submit_button("REGISTRAR COMERCIO"):
            if rn and rm and rt and ri and ref_socio:
                path_i = f"portadas/reg_{random.randint(1000,9999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path_i, ri.getvalue())
                url_i = supabase.storage.from_("fotos_productos").get_public_url(path_i)
                supabase.table("perfiles_comercio").insert({"nombre_comercio": rn, "email_propietario": rm.lower(), "whatsapp": rt, "portada_url": url_i, "plan": plan_sel, "codigo_acceso": "LUXURY7"}).execute()
                st.success("¡Registro Exitoso!")
                st.link_button("📲 NOTIFICAR AL ADMIN", f"https://wa.me/584241234567?text=Nueva Tienda: {rn}")

elif not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        res = supabase.table("perfiles_comercio").select("*").execute()
        tiendas = res.data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2, gap="small")
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        url = t.get('portada_url') or "https://via.placeholder.com/400"
                        st.markdown(f'<img src="{url}" class="img-portada-full">', unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; color:#D4AF37; font-weight:bold;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                        if st.button("VISITAR", key=f"m_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        
        # Columna central para enfoque móvil / vertical
        _, center_col, _ = st.columns([0.1, 0.8, 0.1])
        with center_col:
            for p in prods.data:
                st.markdown(f"""
                <div class="product-card">
                    <div class="price-badge">${p['precio']}</div>
                    <h2 style='color:#F9F295; font-size:1.5rem;'>{p['nombre_producto']}</h2>
                """, unsafe_allow_html=True)
                
                # Video optimizado a 9:16
                st.video(p['video_url'], autoplay=True, loop=True, muted=True)
                
                if st.button(f"🛒 ADQUIRIR {p['nombre_producto']}", key=f"btn_{p['id']}", use_container_width=True):
                    ventana_pago(p, t)
                st.markdown("</div>", unsafe_allow_html=True)

else:
    # --- PANEL ADMIN ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.container(border=True):
            m = st.text_input("Email").strip().lower()
            c = st.text_input("Código", type="password").strip().upper()
            if st.button("🔓 ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == c:
                    st.session_state.logged_in = True; st.session_state.user_email = m; st.rerun()
                else: st.error("Acceso denegado")
    else:
        # Lógica simplificada de gestión para el ejemplo completo
        st.write(f"Sesión activa: **{st.session_state.user_email}**")
        if st.button("🚪 CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()