import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import uuid

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

# Configuración de planes y beneficios
PLANES = {
    "GRATUITO": {"limite": 3, "precio": "0", "color": "#C0C0C0", "beneficios": ["3 Productos", "Video Reels", "Panel Básico", "Soporte Email"]},
    "BRONCE": {"limite": 10, "precio": "5", "color": "#CD7F32", "beneficios": ["10 Productos", "Video Reels", "Panel Pro", "Soporte WhatsApp"]},
    "PLATA": {"limite": 25, "precio": "15", "color": "#E5E4E2", "beneficios": ["25 Productos", "Video Reels", "Estadísticas", "Destacado"]},
    "ORO": {"limite": 100, "precio": "30", "color": "#D4AF37", "beneficios": ["100 Productos", "Video Reels", "Prioridad VIP", "Soporte 24/7"]}
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = []
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

def subir_archivo(file, folder):
    try:
        ext = file.name.split(".")[-1]
        filename = f"{folder}/{uuid.uuid4()}.{ext}"
        supabase.storage.from_("luxury_assets").upload(filename, file.read())
        return supabase.storage.from_("luxury_assets").get_public_url(filename)
    except Exception as e:
        st.error(f"Error al subir: {e}"); return None

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000; color: #fff; }
    .img-redonda {
        width: 180px; height: 180px; border-radius: 50%;
        object-fit: cover; border: 2px solid #D4AF37;
        margin: 0 auto 15px auto; display: block;
        box-shadow: 0px 8px 20px rgba(212, 175, 55, 0.3);
    }
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 10px !important;
        font-weight: 800 !important; height: 48px !important; width: 100% !important;
        border: none !important;
    }
    .btn-carrito-fix > button {
        background: rgba(255,255,255,0.05) !important;
        color: #D4AF37 !important; border: 1px solid #D4AF37 !important;
        margin-bottom: 8px !important; height: 38px !important;
    }
    .product-info { text-align: center; margin: 10px 0; font-size: 1.4rem; font-weight: bold; }
    .price-tag { color: #39FF14; margin-left: 10px; font-weight: 900; }
    .plan-card {
        border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 15px; 
        padding: 20px; text-align: center; background: #0a0a0a; min-height: 380px;
        margin-bottom: 20px;
    }
    .plan-card ul { list-style: none; padding: 0; font-size: 0.85rem; color: #bbb; }
    .plan-card li { margin: 8px 0; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DEL CARRITO
# ==========================================
@st.dialog("🛒 RESUMEN DE COMPRA")
def ventana_carrito():
    if not st.session_state.cart:
        st.write("Tu carrito está vacío.")
        return
    total = sum(item['precio'] * item['cantidad'] for item in st.session_state.cart)
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"**{item['nombre']}**")
        c2.write(f"x{item['cantidad']}")
        c3.write(f"${item['precio']*item['cantidad']:,.2f}")
        if st.button("🗑️", key=f"del_{i}"):
            st.session_state.cart.pop(i); st.rerun()
    st.divider()
    st.subheader(f"Total: ${total:,.2f}")
    t = st.session_state.tienda_actual
    st.info(f"Pagar a: {t.get('datos_pago', 'Consultar por WhatsApp')}")
    ref = st.text_input("Referencia de Pago")
    if st.button("💎 CONFIRMAR PEDIDO") and ref:
        prods_txt = "\n".join([f"• {x['nombre']} (x{x['cantidad']})" for x in st.session_state.cart])
        msj = f"✨ *NUEVO PEDIDO*\n\n🏪 {t['nombre_comercio']}\n📦 *Productos:*\n{prods_txt}\n\n💰 *Total:* ${total:,.2f}\n🎫 *Ref:* {ref}"
        st.session_state.cart = []
        st.link_button("ENVIAR WHATSAPP", f"https://wa.me/{str(t['whatsapp']).strip()}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. RUTAS Y VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_reg = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO CON BENEFICIOS ---
if es_reg:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>BENEFICIOS SOCIOS LUXURY</h1>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (nombre, info) in enumerate(PLANES.items()):
        with cols[i]:
            benef_html = "".join([f"<li>✅ {b}</li>" for b in info['beneficios']])
            st.markdown(f"""
                <div class="plan-card">
                    <h3 style="color:{info['color']};">{nombre}</h3>
                    <h2>${info['precio']}</h2>
                    <hr style="opacity:0.1;">
                    <ul>{benef_html}</ul>
                </div>
            """, unsafe_allow_html=True)
    
    with st.form("registro_socio"):
        st.subheader("Únete al Mall")
        rn = st.text_input("Nombre Comercial")
        re = st.text_input("Email").lower()
        rw = st.text_input("WhatsApp (ej: 58412...)")
        rp = st.selectbox("Elige tu Plan", list(PLANES.keys()))
        rf = st.file_uploader("Foto de Portada (Logo)", type=['jpg', 'png'])
        ref_p = st.text_input("Referencia de pago suscripción")
        if st.form_submit_button("SOLICITAR AFILIACIÓN"):
            if rn and re and rf:
                url = subir_archivo(rf, "portadas")
                cod = str(random.randint(100000, 999999))
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio":rn, "email_propietario":re, "whatsapp":rw,
                    "plan":rp, "portada_url":url, "referencia_pago":ref_p, "codigo_acceso":cod, "activo":False
                }).execute()
                st.success(f"Solicitud enviada. Tu código de acceso será: {cod}")

# --- VISTA: PANEL DE CONTROL ---
elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        e_log = st.text_input("Email").lower()
        c_log = st.text_input("Código", type="password")
        if st.button("INGRESAR"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", e_log).execute()
            if res.data and str(res.data[0]['codigo_acceso']).upper() == c_log.upper():
                st.session_state.logged_in = True; st.session_state.user_email = e_log; st.rerun()
    else:
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        p_data = PLANES.get(perf['plan'].upper(), PLANES["GRATUITO"])
        
        c_res = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
        actual = c_res.count if c_res.count else 0
        st.progress(min(actual/p_data['limite'], 1.0), text=f"Cupo: {actual}/{p_data['limite']} (Plan {perf['plan']})")

        t1, t2, t3 = st.tabs(["📤 SUBIR", "📦 PRODUCTOS", "🖼️ PERFIL"])
        with t1:
            if actual < p_data['limite']:
                with st.form("add_p"):
                    n, p = st.text_input("Nombre"), st.number_input("Precio ($)")
                    v = st.file_uploader("Video MP4", type=['mp4'])
                    if st.form_submit_button("PUBLICAR"):
                        url = subir_archivo(v, "videos")
                        supabase.table("productos").insert({"nombre_producto":n,"precio":p,"video_url":url,"comercio_relacionado":perf['nombre_comercio']}).execute()
                        st.rerun()
        with t2:
            mis_p = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            for mp in mis_p:
                c_n, c_b = st.columns([4,1]); c_n.write(f"**{mp['nombre_producto']}**")
                if c_b.button("Borrar", key=mp['id']):
                    supabase.table("productos").delete().eq("id", mp['id']).execute(); st.rerun()
        with t3:
            st.image(perf['portada_url'], width=100)
            nueva_f = st.file_uploader("Cambiar Portada", type=['jpg','png'])
            if st.button("Guardar Foto") and nueva_f:
                u = subir_archivo(nueva_f, "portadas")
                supabase.table("perfiles_comercio").update({"portada_url":u}).eq("id", perf['id']).execute(); st.rerun()
            d_pago = st.text_area("Datos de Pago", value=perf.get('datos_pago',''))
            if st.button("Actualizar Datos"):
                supabase.table("perfiles_comercio").update({"datos_pago":d_pago}).eq("id", perf['id']).execute()
        
        if st.button("Cerrar Sesión"): st.session_state.logged_in = False; st.rerun()

# --- VISTA: MALL ---
elif st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    busq = st.text_input("🔍 Buscar tiendas o marcas...", "").lower()
    tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
    tiendas = [t for t in tiendas if busq in t['nombre_comercio'].lower()]
    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i+j < len(tiendas):
                t = tiendas[i+j]
                with cols[j]:
                    st.markdown(f'<img src="{t["portada_url"]}" class="img-redonda">', unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align:center; font-weight:bold;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                    if st.button("ENTRAR", key=t['id'], use_container_width=True):
                        st.session_state.tienda_actual = t; ir_a('tienda')

# --- VISTA: TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if st.button("⬅️ VOLVER AL MALL"): st.session_state.cart = []; ir_a('mall')
    
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    for p in prods:
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown(f'<div class="product-info">{p["nombre_producto"].upper()} <span class="price-tag">${p["precio"]}</span></div>', unsafe_allow_html=True)
        
        # Carrito dinámico sumatorio
        cant_items = sum(item['cantidad'] for item in st.session_state.cart)
        if cant_items > 0:
            st.markdown('<div class="btn-carrito-fix">', unsafe_allow_html=True)
            if st.button(f"🛒 VER CARRITO ({cant_items})", key=f"cart_{p['id']}"): ventana_carrito()
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button(f"➕ AÑADIR AL CARRITO", key=f"add_{p['id']}", use_container_width=True):
            found = False
            for item in st.session_state.cart:
                if item['id'] == p['id']: item['cantidad'] += 1; found = True; break
            if not found: st.session_state.cart.append({"id":p['id'], "nombre":p['nombre_producto'], "precio":p['precio'], "cantidad":1})
            st.toast(f"{p['nombre_producto']} añadido 💎"); st.rerun()
        st.divider()