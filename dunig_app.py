import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN DE ALTO RENDIMIENTO
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

PLANES = {
    "BRONCE": 5,
    "PLATINUM": 15,
    "DIAMANTE": 50
}

# --- LÓGICA DE NAVEGACIÓN ---
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

def generar_codigo():
    return ''.join(random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(7))

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        animation: shimmer 5s infinite linear !important;
        color: #000 !important; border-radius: 30px !important;
        font-weight: 800 !important; text-transform: uppercase;
    }
    .luxury-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 20px; padding: 20px; backdrop-filter: blur(10px); margin-bottom: 20px;
    }
    .price-bubble {
        position: absolute; top: 20px; right: 20px;
        background: rgba(0, 0, 0, 0.9); color: #39FF14; 
        padding: 8px 20px; border-radius: 50px;
        font-weight: 900; border: 2px solid #39FF14; z-index: 10;
    }
    .banner-tienda {
        width: 100%; height: 200px; object-fit: cover;
        border-radius: 20px; border: 1px solid #D4AF37;
        margin-bottom: 20px;
    }
    footer {visibility: hidden;} header {visibility: hidden;}
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
    st.metric("TOTAL", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **PAGO:** {tienda.get('datos_pago', 'Consultar')}")
    ref = st.text_input("Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Prod:* {producto['nombre_producto']}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            st.link_button("WHATSAPP", f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}")
        else: st.error("Falta referencia")

# ==========================================
# 4. CUERPO DE LA APP
# ==========================================

if not es_admin:
    # --- VISTA CLIENTE (MALL) ---
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("🔍 Buscar tiendas...")
        res = supabase.table("perfiles_comercio").select("*").execute()
        tiendas = [t for t in res.data if busqueda.lower() in t['nombre_comercio'].lower()]
        
        cols = st.columns(2)
        for idx, t in enumerate(tiendas):
            with cols[idx % 2]:
                st.markdown(f"<div class='luxury-card'>", unsafe_allow_html=True)
                if t.get('portada_url'):
                    st.image(t['portada_url'], use_container_width=True)
                st.markdown(f"<h3 style='text-align:center;'>{t['nombre_comercio'].upper()}</h3>", unsafe_allow_html=True)
                if st.button("VISITAR", key=f"t_{t['id']}", use_container_width=True):
                    st.session_state.tienda_actual = t
                    ir_a('tienda')
                st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER"): ir_a('mall')
        
        # --- ESTO ES LO QUE MUESTRA LA PORTADA ---
        # Buscamos la URL en el diccionario de la tienda actual
        url_portada = t.get('portada_url')
        
        if url_portada:
            # Usamos HTML para que se vea como un banner de lujo
            st.markdown(f'''
                <div style="width: 100%; height: 250px; overflow: hidden; border-radius: 20px; border: 2px solid #D4AF37; margin-bottom: 20px;">
                    <img src="{url_portada}" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
            ''', unsafe_allow_html=True)
        else:
            # Si no tiene foto, ponemos un aviso elegante
            st.info("✨ Bienvenido a esta experiencia Luxury")
            
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        for p in prods.data:
            st.markdown(f"<div style='position: relative;'><div class='price-bubble'>${p['precio']}</div></div>", unsafe_allow_html=True)
            st.video(p['video_url'])
            if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"p_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.divider()

else:
    # --- PANEL ADMIN ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ CONTROL LUXURY</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        # (Lógica de login idéntica a la anterior...)
        st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
        mail_input = st.text_input("Email de Propietario").strip().lower()
        pass_input = st.text_input("Código de Acceso", type="password").strip().upper()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail_input).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).strip().upper() == pass_input:
                    st.session_state.logged_in = True
                    st.session_state.user_email = mail_input
                    st.rerun()
                else: st.error("Acceso denegado")
        with col2:
            if st.button("🔑 RECIBIR LLAVE"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail_input).execute()
                if res.data:
                    u = res.data[0]; cod = u.get('codigo_acceso') or generar_codigo()
                    if not u.get('codigo_acceso'):
                        supabase.table("perfiles_comercio").update({"codigo_acceso": cod}).eq("id", u['id']).execute()
                    tel = str(u['whatsapp']).replace("+", "").strip()
                    msg = urllib.parse.quote(f"*D'UNIG LUXURY*\nTu llave de acceso es: *{cod}*")
                    st.link_button("🟢 VER EN WHATSAPP", f"https://wa.me/{tel}?text={msg}")
                else: st.error("Email no registrado")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # --- PANEL DE GESTIÓN ACTIVO ---
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        if res.data:
            perf = res.data[0]
            plan = str(perf.get('plan', 'BRONCE')).upper()
            limite = PLANES.get(plan, 5)
            res_c = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            total_p = res_c.count if res_c.count is not None else 0
