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
    footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS Y REGISTRO
# ==========================================
@st.dialog("💎 CARRITO D'UNIG LUXURY")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **PAGO:** {tienda.get('datos_pago', 'Consultar')}")
    ref = st.text_input("Ref. de Pago (Solo números)")
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
                st.markdown(f"<div class='luxury-card'><h3 style='text-align:center;'>{t['nombre_comercio'].upper()}</h3>", unsafe_allow_html=True)
                if st.button("VISITAR", key=f"t_{t['id']}", use_container_width=True):
                    st.session_state.tienda_actual = t
                    ir_a('tienda')
                st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER"): ir_a('mall')
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
        st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
        mail = st.text_input("Email de Propietario").strip().lower()
        pass_input = st.text_input("Código de Acceso", type="password").strip().upper()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).strip().upper() == pass_input:
                    st.session_state.logged_in = True
                    st.session_state.user_email = mail
                    st.rerun()
                else: st.error("Acceso denegado")
        
        with col2:
            if st.button("🔑 RECIBIR LLAVE"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
                if res.data:
                    u = res.data[0]
                    cod = u.get('codigo_acceso') or generar_codigo()
                    if not u.get('codigo_acceso'):
                        supabase.table("perfiles_comercio").update({"codigo_acceso": cod}).eq("id", u['id']).execute()
                    
                    tel = str(u['whatsapp']).replace("+", "").strip()
                    msg = urllib.parse.quote(f"*D'UNIG LUXURY*\nTu llave de acceso es: *{cod}*")
                    st.link_button("🟢 VER EN WHATSAPP", f"https://wa.me/{tel}?text={msg}")
                else: st.error("Email no registrado")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # PANEL ACTIVO
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        if res.data:
            perf = res.data[0]
            plan = perf.get('plan', 'BRONCE').upper()
            limite = PLANES.get(plan, 5)
            res_c = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            total_p = res_c.count if res_c.count else 0
            
            st.markdown(f"<div class='luxury-card'><h3>Tienda: {perf['nombre_comercio']}</h3>", unsafe_allow_html=True)
            c_a, c_b = st.columns(2)
            c_a.metric("Plan Actual", plan)
            c_b.metric("Inventario", f"{total_p}/{limite}")
            st.progress(min(total_p/limite, 1.0))
            if st.button("🚪 CERRAR SESIÓN"):
                st.session_state.logged_in = False
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            # --- TABS INCLUYENDO REGISTRO ---
            t1, t2, t3, t4, t5 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS", "💎 MI PLAN", "✨ REGISTRO"])
            
            with t1:
                if total_p >= limite: st.warning("Cupos agotados. Aumenta tu plan en 'MI PLAN'.")
                else:
                    with st.form("p", clear_on_submit=True):
                        n = st.text_input("Nombre del Producto")
                        pr = st.number_input("Precio ($)", min_value=0.0)
                        v = st.file_uploader("Video (MP4)", type=['mp4'])
                        if st.form_submit_button("PUBLICAR"):
                            if n and v:
                                path = f"v/{random.randint(1000,9999)}.mp4"
                                supabase.storage.from_("fotos_productos").upload(path, v.getvalue())
                                url = supabase.storage.from_("fotos_productos").get_public_url(path)
                                supabase.table("productos").insert({"nombre_producto":n, "precio":pr, "video_url":url, "comercio_relacionado":perf['nombre_comercio']}).execute()
                                st.rerun()

            with t2:
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    with st.expander(f"📦 {i['nombre_producto']} - ${i['precio']}"):
                        if st.button("ELIMINAR", key=f"del_{i['id']}"):
                            supabase.table("productos").delete().eq("id", i['id']).execute()
                            st.rerun()

            with t3:
                p_inf = st.text_area("Información para pagos", value=str(perf.get('datos_pago', '')))
                if st.button("ACTUALIZAR DATOS"):
                    supabase.table("perfiles_comercio").update({"datos_pago": p_inf}).eq("id", perf['id']).execute()
                    st.success("Datos guardados")

            with t4:
                st.markdown("### 🚀 Aumenta tu capacidad")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**PLAN PLATINUM**\n- 15 Cupos")
                    st.link_button("💎 SUBIR A PLATINUM", f"https://wa.me/{perf['whatsapp']}?text=Deseo_Platinum")
                with c2:
                    st.markdown("**PLAN DIAMANTE**\n- 50 Cupos")
                    st.link_button("👑 SUBIR A DIAMANTE", f"https://wa.me/{perf['whatsapp']}?text=Deseo_Diamante")

            with t5:
                st.markdown("### 🆕 Registrar Nuevo Propietario")
                with st.form("reg_nuevo"):
                    reg_nom = st.text_input("Nombre de la Tienda").strip()
                    reg_mail = st.text_input("Email Propietario").strip().lower()
                    reg_tel = st.text_input("WhatsApp (Ej: 58412...)").strip()
                    reg_plan = st.selectbox("Asignar Plan", ["BRONCE", "PLATINUM", "DIAMANTE"])
                    if st.form_submit_button("💎 REGISTRAR TIENDA"):
                        if reg_nom and reg_mail and reg_tel:
                            supabase.table("perfiles_comercio").insert({
                                "nombre_comercio": reg_nom,
                                "email_propietario": reg_mail,
                                "whatsapp": reg_tel,
                                "plan": reg_plan
                            }).execute()
                            st.success(f"Tienda {reg_nom} creada con éxito.")
                        else: st.error("Llenar campos obligatorios.")
        else: st.error("Error de sesión")
