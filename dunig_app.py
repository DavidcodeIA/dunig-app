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

# Configuración de límites según tu corrección
PLANES = {
    "GRATUITO": {"limite": 3, "precio": "0", "color": "#C0C0C0"},
    "BRONCE": {"limite": 10, "precio": "5", "color": "#CD7F32"},
    "PLATA": {"limite": 25, "precio": "15", "color": "#E5E4E2"},
    "ORO": {"limite": 100, "precio": "30", "color": "#D4AF37"}
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

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
        st.error(f"Error en la subida: {e}"); return None

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
    }

    .product-info { text-align: center; margin: 15px 0; font-size: 1.5rem; font-weight: bold; }
    .price-tag { color: #39FF14; margin-left: 12px; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO CON PLANES ---
if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>💎 PLANES DE EXPANSIÓN</h1>", unsafe_allow_html=True)
    
    # Mostrar Beneficios
    cols_planes = st.columns(4)
    for i, (nombre, info) in enumerate(PLANES.items()):
        with cols_planes[i]:
            st.markdown(f"""
                <div class="plan-card">
                    <h3 style="color:{info['color']};">{nombre}</h3>
                    <h2 style="margin:0;">${info['precio']}</h2>
                    <p style="color:gray;">al mes</p>
                    <hr style="border-color:rgba(212,175,55,0.2);">
                    <p><b>{info['limite']}</b> Productos</p>
                    <p>Soporte Luxury</p>
                    <p>Panel Admin</p>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    with st.form("form_registro"):
        st.subheader("Formulario de Inscripción")
        rn = st.text_input("Nombre de la Tienda")
        rm = st.text_input("Correo del Propietario")
        rt = st.text_input("WhatsApp (ej: 58412...)")
        plan_sel = st.selectbox("Elige tu Plan", options=list(PLANES.keys()))
        ri = st.file_uploader("Foto de Portada", type=['jpg', 'png'])
        ref_p = st.text_input("Referencia de Pago de Activación")
        
        if st.form_submit_button("SOLICITAR ACTIVACIÓN"):
            if rn and rm and ri:
                with st.spinner("Procesando..."):
                    url_p = subir_archivo(ri, "portadas")
                    cod = str(random.randint(100000, 999999))
                    supabase.table("perfiles_comercio").insert({
                        "nombre_comercio": rn, "email_propietario": rm.lower(),
                        "whatsapp": rt, "plan": plan_sel, "portada_url": url_p,
                        "referencia_pago": ref_p, "codigo_acceso": cod, "activo": False
                    }).execute()
                    st.success(f"¡Solicitud enviada! Tu código es: {cod}")

# --- VISTA: PANEL DE CONTROL ---
elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ GESTIÓN DE SOCIO</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        m = st.text_input("Email").lower()
        c = st.text_input("Código", type="password")
        if st.button("ENTRAR"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
            if res.data and str(res.data[0]['codigo_acceso']).upper() == c.upper():
                st.session_state.logged_in = True; st.session_state.user_email = m; st.rerun()
    else:
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        
        # Barra Estadística
        c_res = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
        actual = c_res.count if c_res.count else 0
        limite = PLANES[perf['plan']]['limite']
        st.progress(min(actual/limite, 1.0), text=f"Cupos: {actual} de {limite} (Plan {perf['plan']})")

        tab1, tab2, tab3 = st.tabs(["📤 CARGAR PRODUCTO", "🗑️ PRODUCTOS", "🖼️ PERFIL"])
        
        with tab1:
            if actual < limite:
                with st.form("cargar"):
                    n, p = st.text_input("Nombre"), st.number_input("Precio ($)", min_value=0.0)
                    v = st.file_uploader("Video", type=['mp4'])
                    if st.form_submit_button("SUBIR"):
                        url = subir_archivo(v, "videos")
                        supabase.table("productos").insert({"nombre_producto":n,"precio":p,"video_url":url,"comercio_relacionado":perf['nombre_comercio']}).execute()
                        st.rerun()
            else: st.error("Límite de plan alcanzado.")

        with tab2:
            prods = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            for pr in prods:
                c1, c2 = st.columns([4,1])
                c1.write(f"📦 {pr['nombre_producto']}")
                if c2.button("BORRAR", key=pr['id']):
                    supabase.table("productos").delete().eq("id", pr['id']).execute()
                    st.rerun()

        with tab3:
            st.image(perf['portada_url'], width=100)
            nueva = st.file_uploader("Editar Portada", type=['jpg','png'])
            if st.button("ACTUALIZAR") and nueva:
                url = subir_archivo(nueva, "portadas")
                supabase.table("perfiles_comercio").update({"portada_url": url}).eq("id", perf['id']).execute()
                st.rerun()
            
            datos = st.text_area("Datos de Pago", value=perf.get('datos_pago',''))
            if st.button("GUARDAR PAGO"):
                supabase.table("perfiles_comercio").update({"datos_pago": datos}).eq("id", perf['id']).execute()

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
                    st.markdown(f"<p style='text-align:center;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                    if st.button("ENTRAR", key=f"t_{t['id']}", use_container_width=True):
                        st.session_state.tienda_actual = t; ir_a('tienda')

# --- VISTA: TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if st.button("⬅️ REGRESAR"): ir_a('mall')
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    for p in prods:
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown(f'<div class="product-info">{p["nombre_producto"].upper()} <span class="price-tag">${p["precio"]}</span></div>', unsafe_allow_html=True)
        # Diálogo de compra omitido por brevedad pero funcional con el botón
        if st.button(f"🛒 COMPRAR", key=p['id'], use_container_width=True):
            st.info(f"Contacta al vendedor. Datos: {t.get('datos_pago')}")
        st.divider()