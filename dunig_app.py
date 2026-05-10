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

# Configuración extendida de planes y beneficios
PLANES = {
    "GRATUITO": {
        "limite": 3, "precio": "0", "color": "#C0C0C0",
        "beneficios": ["3 Productos", "Video Reels", "Panel Básico", "Soporte Email"]
    },
    "BRONCE": {
        "limite": 10, "precio": "5", "color": "#CD7F32",
        "beneficios": ["10 Productos", "Video Reels", "Panel Pro", "Soporte WhatsApp"]
    },
    "PLATA": {
        "limite": 25, "precio": "15", "color": "#E5E4E2",
        "beneficios": ["25 Productos", "Video Reels", "Estadísticas", "Destacado Bronce"]
    },
    "ORO": {
        "limite": 100, "precio": "30", "color": "#D4AF37",
        "beneficios": ["100 Productos", "Video Reels", "Estadísticas Full", "Prioridad en Mall"]
    }
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = []

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
        st.error(f"Error: {e}"); return None

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000; color: #fff; }
    .img-redonda {
        width: 200px; height: 200px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 15px auto; display: block;
        box-shadow: 0px 10px 25px rgba(212, 175, 55, 0.4);
    }
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; height: 50px !important; width: 100% !important;
    }
    .plan-card {
        border: 1px solid rgba(212, 175, 55, 0.4); border-radius: 15px; 
        padding: 20px; text-align: center; background: #111;
        margin-bottom: 10px; min-height: 380px;
    }
    .plan-card ul { list-style: none; padding: 0; font-size: 0.85rem; color: #ccc; }
    .plan-card li { margin: 8px 0; }
    .product-info { text-align: center; margin: 15px 0; font-size: 1.5rem; font-weight: bold; }
    .price-tag { color: #39FF14; margin-left: 12px; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. COMPONENTE: CARRITO
# ==========================================
@st.dialog("🛒 TU CARRITO")
def ventana_carrito():
    if not st.session_state.cart:
        st.write("Tu carrito está vacío.")
        return
    total = 0
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3 = st.columns([3, 1, 1])
        sub = item['precio'] * item['cantidad']
        total += sub
        c1.write(f"**{item['nombre']}**")
        c2.write(f"x{item['cantidad']}")
        c3.write(f"${sub:,.2f}")
        if st.button("🗑️", key=f"del_{i}"):
            st.session_state.cart.pop(i); st.rerun()
    st.divider()
    st.subheader(f"Total: ${total:,.2f}")
    t = st.session_state.tienda_actual
    ref = st.text_input("Referencia de Pago")
    if st.button("💎 PAGAR Y NOTIFICAR") and ref:
        prods_txt = "\n".join([f"- {x['nombre']} (x{x['cantidad']})" for x in st.session_state.cart])
        msj = f"✨ *PEDIDO*\n\n🏪 {t['nombre_comercio']}\n📦 *Productos:*\n{prods_txt}\n\n💰 *Total:* ${total:,.2f}\n🎫 *Ref:* {ref}"
        st.session_state.cart = []
        st.link_button("WHATSAPP", f"https://wa.me/{str(t['whatsapp']).strip()}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_reg = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO CON TABLA DE BENEFICIOS ---
if es_reg:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ ELIGE TU NIVEL LUXURY</h1>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (nombre, info) in enumerate(PLANES.items()):
        with cols[i]:
            beneficios_html = "".join([f"<li>✅ {b}</li>" for b in info['beneficios']])
            st.markdown(f"""
                <div class="plan-card">
                    <h3 style="color:{info['color']};">{nombre}</h3>
                    <h2 style="margin:0;">${info['precio']}</h2>
                    <p style="color:gray; font-size:0.8rem;">pago mensual</p>
                    <hr style="opacity:0.2;">
                    <ul>{beneficios_html}</ul>
                </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    with st.form("reg_form"):
        st.subheader("Formulario de Registro")
        rn, rm, rt = st.text_input("Nombre de Tienda"), st.text_input("Email"), st.text_input("WhatsApp")
        ps = st.selectbox("Plan", list(PLANES.keys()))
        ri = st.file_uploader("Portada", type=['jpg', 'png'])
        ref = st.text_input("Referencia de Pago Suscripción")
        if st.form_submit_button("REGISTRARME"):
            url = subir_archivo(ri, "portadas")
            cod = str(random.randint(100000, 999999))
            supabase.table("perfiles_comercio").insert({
                "nombre_comercio":rn, "email_propietario":rm.lower(), "whatsapp":rt,
                "plan":ps, "portada_url":url, "referencia_pago":ref, "codigo_acceso":cod, "activo":False
            }).execute()
            st.success(f"Solicitud enviada. Tu código de acceso es: {cod}")

# --- VISTA: PANEL ADMIN ---
elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        m, c = st.text_input("Email"), st.text_input("Código", type="password")
        if st.button("ACCEDER"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m.lower()).execute()
            if res.data and str(res.data[0]['codigo_acceso']).upper() == c.upper():
                st.session_state.logged_in = True; st.session_state.user_email = m; st.rerun()
    else:
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        nombre_plan = str(perf.get('plan', 'GRATUITO')).upper().strip()
        limite = PLANES.get(nombre_plan, PLANES["GRATUITO"])['limite']
        
        c_res = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
        actual = c_res.count if c_res.count else 0
        st.progress(min(actual/limite, 1.0), text=f"{actual} de {limite} productos usados (Plan {nombre_plan})")

        t1, t2, t3 = st.tabs(["📤 CARGAR", "🗑️ PRODUCTOS", "🖼️ PERFIL"])
        with t1:
            if actual < limite:
                with st.form("add"):
                    n, p = st.text_input("Nombre"), st.number_input("Precio ($)")
                    v = st.file_uploader("Video", type=['mp4'])
                    if st.form_submit_button("SUBIR"):
                        url = subir_archivo(v, "videos")
                        supabase.table("productos").insert({"nombre_producto":n,"precio":p,"video_url":url,"comercio_relacionado":perf['nombre_comercio']}).execute()
                        st.rerun()
        with t2:
            prods = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            for pr in prods:
                c1, c2 = st.columns([4,1]); c1.write(f"📦 {pr['nombre_producto']}"); 
                if c2.button("Borrar", key=pr['id']):
                    supabase.table("productos").delete().eq("id", pr['id']).execute(); st.rerun()
        with t3:
            st.image(perf['portada_url'], width=100)
            nueva = st.file_uploader("Nueva Portada", type=['jpg','png'])
            if st.button("Guardar Foto") and nueva:
                u = subir_archivo(nueva, "portadas")
                supabase.table("perfiles_comercio").update({"portada_url":u}).eq("id", perf['id']).execute(); st.rerun()
            dat = st.text_area("Datos Pago", value=perf.get('datos_pago',''))
            if st.button("Guardar Datos Pago"):
                supabase.table("perfiles_comercio").update({"datos_pago":dat}).eq("id", perf['id']).execute()

# --- VISTA: MALL ---
elif st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    busq = st.text_input("🔍 Buscar tiendas...", "").lower()
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
    c1, c2 = st.columns([3,1])
    with c1: 
        if st.button("⬅️ VOLVER"): st.session_state.cart = []; ir_a('mall')
    with c2:
        if st.button(f"🛒 ({len(st.session_state.cart)})"): ventana_carrito()
    
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    for p in prods:
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown(f'<div class="product-info">{p["nombre_producto"].upper()} <span class="price-tag">${p["precio"]}</span></div>', unsafe_allow_html=True)
        cant = st.number_input("Cant.", 1, 10, 1, key=f"q_{p['id']}")
        if st.button(f"➕ AÑADIR", key=p['id'], use_container_width=True):
            st.session_state.cart.append({"id":p['id'],"nombre":p['nombre_producto'],"precio":p['precio'],"cantidad":cant})
            st.toast("¡Añadido!")
            st.rerun()
        st.divider()