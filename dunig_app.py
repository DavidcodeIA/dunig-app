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

# Configuración de límites y beneficios
PLANES = {
    "GRATUITO": {"limite": 3, "precio": "0", "color": "#C0C0C0"},
    "BRONCE": {"limite": 10, "precio": "5", "color": "#CD7F32"},
    "PLATA": {"limite": 25, "precio": "15", "color": "#E5E4E2"},
    "ORO": {"limite": 100, "precio": "30", "color": "#D4AF37"}
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

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
        st.error(f"Error en subida: {e}")
        return None

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000000; color: #ffffff; }
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
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 50px !important; width: 100% !important;
    }
    .plan-card {
        border: 1px solid #D4AF37; border-radius: 15px; padding: 20px;
        text-align: center; background: rgba(255,255,255,0.05); margin-bottom: 20px;
        min-height: 280px;
    }
    .product-info { text-align: center; margin: 15px 0; font-size: 1.5rem; font-weight: bold; }
    .price-tag { color: #39FF14; margin-left: 12px; font-weight: 900; }
    .btn-regresar button {
        background: transparent !important; color: #ffffff !important; 
        border: 1px solid rgba(255,255,255,0.3) !important;
        height: 35px !important; font-size: 0.8rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE NAVEGACIÓN
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO ---
if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>💎 SELECCIONA TU PLAN</h1>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (nombre, info) in enumerate(PLANES.items()):
        with cols[i]:
            st.markdown(f'<div class="plan-card"><h3 style="color:{info["color"]}">{nombre}</h3><h2>${info["precio"]}</h2><hr><p><b>{info["limite"]}</b> Productos</p><p>Video Reels</p></div>', unsafe_allow_html=True)
    
    st.divider()
    with st.form("registro_socio"):
        rn = st.text_input("Nombre de la Tienda")
        rm = st.text_input("Email del Dueño")
        rt = st.text_input("WhatsApp (ej: 58412...)")
        ps = st.selectbox("Elige tu Plan", options=list(PLANES.keys()))
        ri = st.file_uploader("Logo/Portada", type=['jpg', 'png'])
        ref = st.text_input("Referencia de Pago de Activación")
        
        if st.form_submit_button("SOLICITAR ACTIVACIÓN"):
            if rn and rm and rt and ri:
                url_img = subir_archivo(ri, "portadas")
                cod = str(random.randint(100000, 999999))
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": rn, "email_propietario": rm.lower(), "whatsapp": rt,
                    "plan": ps, "portada_url": url_img, "referencia_pago": ref,
                    "codigo_acceso": cod, "activo": False
                }).execute()
                st.success(f"¡Solicitud enviada! Código: {cod}")

# --- VISTA: PANEL DE CONTROL ---
elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE SOCIO</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        email_in = st.text_input("Email").lower()
        pass_in = st.text_input("Código", type="password")
        if st.button("ACCEDER"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_in).execute()
            if res.data and str(res.data[0]['codigo_acceso']).upper() == pass_in.upper():
                st.session_state.logged_in = True
                st.session_state.user_email = email_in
                st.rerun()
            else: st.error("Acceso denegado.")
    else:
        # Obtener datos y prevenir KeyError
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        nombre_plan = str(perf.get('plan', 'GRATUITO')).upper().strip()
        info_plan = PLANES.get(nombre_plan, PLANES["GRATUITO"])
        limite = info_plan['limite']

        # Estadísticas
        c_res = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
        actual = c_res.count if c_res.count else 0
        st.progress(min(actual/limite, 1.0), text=f"Cupos: {actual} de {limite} (Plan {nombre_plan})")

        t1, t2, t3 = st.tabs(["📤 CARGAR", "🗑️ INVENTARIO", "🖼️ PERFIL"])
        with t1:
            if actual < limite:
                with st.form("cargar_p", clear_on_submit=True):
                    np, pp = st.text_input("Nombre"), st.number_input("Precio ($)")
                    vp = st.file_uploader("Video MP4", type=['mp4'])
                    if st.form_submit_button("PUBLICAR"):
                        v_url = subir_archivo(vp, "videos")
                        supabase.table("productos").insert({"nombre_producto":np, "precio":pp, "video_url":v_url, "comercio_relacionado":perf['nombre_comercio']}).execute()
                        st.rerun()
            else: st.warning("Plan lleno.")
        
        with t2:
            st.subheader("Gestionar Productos")
            mis_prods = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            for p in mis_prods:
                col_n, col_b = st.columns([4,1])
                col_n.write(f"🎥 {p['nombre_producto']} (${p['precio']})")
                if col_b.button("BORRAR", key=f"del_{p['id']}"):
                    supabase.table("productos").delete().eq("id", p['id']).execute()
                    st.rerun()

        with t3:
            st.subheader("Editar Portada y Pagos")
            st.image(perf['portada_url'], width=100)
            nueva_img = st.file_uploader("Cambiar Imagen", type=['jpg','png'])
            if st.button("GUARDAR IMAGEN") and nueva_img:
                u = subir_archivo(nueva_img, "portadas")
                supabase.table("perfiles_comercio").update({"portada_url": u}).eq("id", perf['id']).execute()
                st.rerun()
            dp = st.text_area("Datos de Cobro", value=perf.get('datos_pago', ''))
            if st.button("GUARDAR DATOS DE PAGO"):
                supabase.table("perfiles_comercio").update({"datos_pago": dp}).eq("id", perf['id']).execute()
                st.success("Actualizado")

# --- VISTA: MALL ---
elif st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
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
    st.markdown('<div class="btn-regresar">', unsafe_allow_html=True)
    if st.button("⬅️ REGRESAR AL MALL"): ir_a('mall')
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    for p in prods:
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown(f'<div class="product-info">{p["nombre_producto"].upper()} <span class="price-tag">${p["precio"]}</span></div>', unsafe_allow_html=True)
        if st.button(f"🛒 COMPRAR", key=p['id'], use_container_width=True):
            st.info(f"Instrucciones de Pago: {t.get('datos_pago', 'Consultar por WhatsApp')}")
            msj = f"¡Hola! Quiero comprar: {p['nombre_producto']} (${p['precio']})"
            st.link_button("CONTACTAR POR WHATSAPP", f"https://wa.me/{str(t['whatsapp']).strip()}?text={urllib.parse.quote(msj)}")
        st.divider()