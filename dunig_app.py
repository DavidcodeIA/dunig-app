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

PLANES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 100}

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
        st.error(f"Error: {e}"); return None

# ==========================================
# 2. ESTÉTICA LUXURY ACTUALIZADA (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000000; color: #ffffff; }
    
    /* Círculos de Comercios más grandes */
    .img-redonda {
        width: 200px; height: 200px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 15px auto; display: block;
        box-shadow: 0px 10px 20px rgba(212, 175, 55, 0.3);
    }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 50px !important; width: 100% !important;
    }

    .btn-regresar button {
        background: transparent !important; color: #ffffff !important; 
        border: 1px solid rgba(255,255,255,0.3) !important;
        height: 30px !important; font-size: 0.75rem !important;
    }

    /* Estilo para Nombre y Precio en la misma línea */
    .product-info {
        text-align: center; margin: 15px 0; font-size: 1.4rem; font-weight: bold;
    }
    .price-tag {
        color: #39FF14; margin-left: 10px; font-weight: 900;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS Y VISTAS
# ==========================================
@st.dialog("💎 PROCESAR COMPRA")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cant = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cant
    st.metric("TOTAL", f"${total:,.2f}")
    st.info(tienda.get('datos_pago', 'No configurado'))
    ref = st.text_input("Referencia de Pago")
    if st.button("🚀 CONFIRMAR WHATSAPP"):
        if ref:
            msj = f"✨ *PEDIDO*\n📦 {producto['nombre_producto']}\n💰 Total: ${total}\n🎫 Ref: {ref}"
            st.link_button("ABRIR WA", f"https://wa.me/{str(tienda['whatsapp']).strip()}?text={urllib.parse.quote(msj)}")

es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

# --- REGISTRO ---
if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO</h1>", unsafe_allow_html=True)
    with st.form("reg"):
        rn, rm, rt = st.text_input("Tienda"), st.text_input("Email"), st.text_input("WhatsApp")
        plan = st.selectbox("Plan", options=list(PLANES.keys()))
        ri = st.file_uploader("Foto", type=['jpg', 'png'])
        ref = st.text_input("Ref. Pago")
        if st.form_submit_button("REGISTRAR"):
            url = subir_archivo(ri, "portadas")
            cod = str(random.randint(100000, 999999))
            supabase.table("perfiles_comercio").insert({"nombre_comercio":rn,"email_propietario":rm.lower(),"whatsapp":rt,"plan":plan,"portada_url":url,"referencia_pago":ref,"codigo_acceso":cod,"activo":False}).execute()
            st.success(f"Código: {cod}")

# --- ADMIN ---
elif es_admin:
    if not st.session_state.logged_in:
        m, c = st.text_input("Email"), st.text_input("Código", type="password")
        if st.button("ENTRAR"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
            if res.data and str(res.data[0]['codigo_acceso']).upper() == c.upper():
                st.session_state.logged_in = True; st.session_state.user_email = m; st.rerun()
    else:
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        t1, t2, t3 = st.tabs(["📦 PRODUCTOS", "🖼️ PORTADA", "💳 PAGOS"])
        with t1:
            if st.button("BORRAR SELECCIONADO"): pass # Lógica de borrado aquí
            with st.form("add_p", clear_on_submit=True):
                np, pp, vp = st.text_input("Nombre"), st.number_input("Precio"), st.file_uploader("Video", type=['mp4'])
                if st.form_submit_button("SUBIR"):
                    url = subir_archivo(vp, "videos")
                    supabase.table("productos").insert({"nombre_producto":np,"precio":pp,"video_url":url,"comercio_relacionado":perf['nombre_comercio']}).execute()
                    st.rerun()
        with t3:
            d = st.text_area("Datos", value=perf.get('datos_pago',''))
            if st.button("GUARDAR"):
                supabase.table("perfiles_comercio").update({"datos_pago":d}).eq("id", perf['id']).execute()

# --- MALL ---
elif st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(tiendas):
                t = tiendas[i+j]
                with cols[j]:
                    st.markdown(f'<img src="{t["portada_url"]}" class="img-redonda">', unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align:center; font-weight:bold;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                    if st.button("ENTRAR", key=t['id'], use_container_width=True):
                        st.session_state.tienda_actual = t; ir_a('tienda')

# --- TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.markdown('<div class="btn-regresar">', unsafe_allow_html=True)
    if st.button("⬅️ REGRESAR AL MALL"): ir_a('mall')
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    for p in prods:
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        # Nombre y Precio en la misma línea
        st.markdown(f'''
            <div class="product-info">
                {p['nombre_producto'].upper()} <span class="price-tag">${p['precio']}</span>
            </div>
        ''', unsafe_allow_html=True)
        if st.button(f"🛒 COMPRAR", key=p['id'], use_container_width=True):
            ventana_pago(p, t)
        st.divider()