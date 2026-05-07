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
        
        # Banner de Portada
        if t.get('portada_url'):
            st.markdown(f'<img src="{t["portada_url"]}" class="banner-tienda">', unsafe_allow_html=True)
            
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
            
            st.markdown(f"<div class='luxury-card'><h3>Tienda: {perf['nombre_comercio']}</h3>", unsafe_allow_html=True)
            c_a, c_b = st.columns(2)
            c_a.metric("Plan", plan); c_b.metric("Cupos", f"{total_p}/{limite}")
            if st.button("🚪 CERRAR SESIÓN"):
                st.session_state.logged_in = False; st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            t1, t2, t3, t4, t5, t6 = st.tabs(["➕ PROD", "📦 GESTIÓN", "💳 COBROS", "🖼️ PORTADA", "💎 PLAN", "✨ REG"])
            
            with t1: # Agregar Producto
                if total_p >= limite: st.warning("Cupos agotados.")
                else:
                    with st.form("p", clear_on_submit=True):
                        n = st.text_input("Nombre"); pr = st.number_input("Precio"); v = st.file_uploader("Video", type=['mp4'])
                        if st.form_submit_button("PUBLICAR"):
                            if n and v:
                                path = f"v/{random.randint(1000,9999)}.mp4"
                                supabase.storage.from_("fotos_productos").upload(path, v.getvalue())
                                url = supabase.storage.from_("fotos_productos").get_public_url(path)
                                supabase.table("productos").insert({"nombre_producto":n, "precio":pr, "video_url":url, "comercio_relacionado":perf['nombre_comercio']}).execute()
                                st.rerun()

            with t2: # Gestión
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    with st.expander(f"{i['nombre_producto']}"):
                        if st.button("ELIMINAR", key=f"del_{i['id']}"):
                            supabase.table("productos").delete().eq("id", i['id']).execute(); st.rerun()

            with t3: # Cobros
                p_inf = st.text_area("Datos de pago", value=str(perf.get('datos_pago', '')))
                if st.button("GUARDAR COBROS"):
                    supabase.table("perfiles_comercio").update({"datos_pago": p_inf}).eq("id", perf['id']).execute(); st.success("Guardado")

            with t4: # NUEVA: PORTADA
                st.markdown("### Configurar Imagen de Portada")
                if perf.get('portada_url'):
                    st.image(perf['portada_url'], caption="Portada Actual", width=300)
                
                img_file = st.file_uploader("Subir Nueva Portada (JPG/PNG)", type=['jpg', 'png', 'jpeg'])
                if st.button("ACTUALIZAR PORTADA"):
                    if img_file:
                        path_img = f"portadas/{perf['id']}_{random.randint(100,999)}.jpg"
                        supabase.storage.from_("fotos_productos").upload(path_img, img_file.getvalue())
                        url_img = supabase.storage.from_("fotos_productos").get_public_url(path_img)
                        supabase.table("perfiles_comercio").update({"portada_url": url_img}).eq("id", perf['id']).execute()
                        st.success("¡Portada actualizada!")
                        st.rerun()

            with t5: # Planes
                st.write("Mejorar a Platinum o Diamante vía WhatsApp.")
                st.link_button("💎 CONTACTAR SOPORTE", f"https://wa.me/TU_NUMERO")

            with t6: # Registro (Solo para crear nuevos)
                with st.form("reg_nuevo"):
                    r_n = st.text_input("Tienda"); r_m = st.text_input("Email"); r_t = st.text_input("WA")
                    if st.form_submit_button("REGISTRAR"):
                        supabase.table("perfiles_comercio").insert({"nombre_comercio":r_n, "email_propietario":r_m.lower(), "whatsapp":r_t, "plan":"BRONCE"}).execute()
                        st.success("Creado")
