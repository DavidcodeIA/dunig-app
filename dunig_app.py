import streamlit as st
from supabase import create_client, Client
import urllib.parse
import uuid
import random

# ==========================================
# 1. CONFIGURACIÓN, CONEXIÓN Y UTILIDADES
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
        st.error(f"Error en carga: {e}")
        return None

# ==========================================
# 2. ESTÉTICA LUXURY (CSS CONSOLIDADO)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000; color: #fff; }
    .img-redonda {
        width: 200px; height: 200px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 15px auto; display: block;
        box-shadow: 0px 10px 25px rgba(212,175,55,0.2);
    }
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 50px !important; width: 100% !important;
    }
    .btn-regresar button {
        background: transparent !important; color: #fff !important; 
        border: 1px solid rgba(255,255,255,0.3) !important;
        height: 32px !important; font-size: 0.75rem !important;
    }
    .product-title { text-align: center; color: #D4AF37; font-size: 1.5rem; margin-top: 10px; font-weight: bold; }
    .product-price { color: #39FF14; font-weight: 800; margin-left: 12px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DE COMPRA
# ==========================================
@st.dialog("💎 DETALLES DE COMPRA")
def ventana_pago(producto, tienda):
    st.markdown(f"### {producto['nombre_producto']}")
    cant = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cant
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **DATOS DE PAGO:**\n{tienda.get('datos_pago', 'Consultar al vendedor')}")
    ref = st.text_input("Referencia de Pago")
    if st.button("CONFIRMAR PEDIDO"):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Producto:* {producto['nombre_producto']}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("ENVIAR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else: st.error("Falta la referencia")

# ==========================================
# 4. LÓGICA DE NAVEGACIÓN
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO ---
if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE SOCIO</h1>", unsafe_allow_html=True)
    with st.form("registro_socio", clear_on_submit=True):
        rn = st.text_input("Nombre de la Tienda")
        rm = st.text_input("Email")
        rt = st.text_input("WhatsApp (Ej: 58412...)")
        plan_sel = st.selectbox("Plan", options=list(PLANES.keys()))
        ri = st.file_uploader("Logo/Portada", type=['jpg', 'png'])
        ref_pago = st.text_input("Referencia Pago Activación")
        if st.form_submit_button("SOLICITAR ACTIVACIÓN"):
            if rn and rm and rt and ri:
                url = subir_archivo(ri, "portadas")
                cod = str(random.randint(100000, 999999))
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": rn, "email_propietario": rm.lower(), 
                    "whatsapp": rt, "plan": plan_sel, "portada_url": url, 
                    "referencia_pago": ref_pago, "codigo_acceso": cod, "activo": False
                }).execute()
                st.success(f"¡Enviado! Tu código de acceso es: {cod}")

# --- VISTA: ADMIN ---
elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL ADMIN</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        m = st.text_input("Email").lower()
        c = st.text_input("Código", type="password")
        if st.button("ENTRAR"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
            if res.data and str(res.data[0]['codigo_acceso']).upper() == c.upper():
                st.session_state.logged_in = True
                st.session_state.user_email = m
                st.rerun()
    else:
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        t1, t2, t3 = st.tabs(["📦 PRODUCTOS", "🖼️ PERFIL", "💳 COBROS"])
        with t1:
            c_res = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            actual, limite = (c_res.count if c_res.count else 0), PLANES.get(perf['plan'], 3)
            st.write(f"Cupos: {actual} / {limite}")
            if actual < limite:
                with st.form("add"):
                    np, pp = st.text_input("Nombre"), st.number_input("Precio")
                    vp = st.file_uploader("Video", type=['mp4'])
                    if st.form_submit_button("PUBLICAR"):
                        v_url = subir_archivo(vp, "videos")
                        supabase.table("productos").insert({"nombre_producto": np, "precio": pp, "video_url": v_url, "comercio_relacionado": perf['nombre_comercio']}).execute()
                        st.rerun()
            for p in supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data:
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"🎥 {p['nombre_producto']} (${p['precio']})")
                if col_b.button("🗑️", key=p['id']):
                    supabase.table("productos").delete().eq("id", p['id']).execute()
                    st.rerun()
        with t2:
            st.subheader("Cambiar Portada")
            if perf['portada_url']: st.image(perf['portada_url'], width=150)
            nf = st.file_uploader("Nueva Foto", type=['jpg', 'png'])
            if st.button("GUARDAR"):
                url = subir_archivo(nf, "portadas")
                supabase.table("perfiles_comercio").update({"portada_url": url}).eq("id", perf['id']).execute()
                st.rerun()
        with t3:
            dp = st.text_area("Datos Pago", value=perf.get('datos_pago', ''))
            if st.button("ACTUALIZAR"):
                supabase.table("perfiles_comercio").update({"datos_pago": dp}).eq("id", perf['id']).execute()
                st.success("Guardado")

# --- VISTA: MALL ---
elif st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(tiendas):
                t = tiendas[i + j]
                with cols[j]:
                    st.markdown(f'<img src="{t["portada_url"]}" class="img-redonda">', unsafe_allow_html=True)
                    if st.button(f"ENTRAR {t['nombre_comercio'].upper()}", key=t['id'], use_container_width=True):
                        st.session_state.tienda_actual = t
                        ir_a('tienda')

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
        st.markdown(f'<div class="product-title">{p["nombre_producto"].upper()} <span class="product-price">${p["precio"]}</span></div>', unsafe_allow_html=True)
        if st.button(f"🛒 COMPRAR AHORA", key=p['id'], use_container_width=True):
            ventana_pago(p, t)
        st.divider()