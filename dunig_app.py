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
# 2. ESTÉTICA INMERSIVA TIKTOK (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Fondo negro puro */
    .main { background-color: #000000; color: #ffffff; padding: 0; }
    
    /* Contenedor del Mall (Portadas Cuadradas) */
    .img-portada-full {
        width: 100%; aspect-ratio: 1 / 1; object-fit: cover;
        border: 1px solid #D4AF37; border-radius: 0px;
    }

    /* Vitrina Full Screen (9:16) */
    .video-wrapper {
        position: relative;
        width: 100%;
        max-width: 500px; /* Centrado para móvil */
        margin: 0 auto;
        aspect-ratio: 9 / 16;
        overflow: hidden;
    }

    /* Video sin bordes redondeados */
    .stVideo { width: 100% !important; border-radius: 0px !important; }
    .stVideo video { object-fit: cover !important; border-radius: 0px !important; }

    /* Burbuja de Precio flotante */
    .overlay-price {
        position: absolute; top: 30px; right: 20px;
        background: linear-gradient(135deg, #D4AF37, #F9F295);
        color: #000; padding: 6px 15px; border-radius: 50px;
        font-weight: 900; font-size: 1.5rem; z-index: 99;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }

    /* Nombre del producto flotante */
    .overlay-name {
        position: absolute; bottom: 30px; left: 20px;
        color: #ffffff; font-size: 1.8rem; font-weight: 800;
        text-shadow: 3px 3px 10px rgba(0,0,0,1); z-index: 99;
        text-transform: uppercase;
    }

    /* Botón de Compra Luxury */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 0px !important;
        font-weight: 800 !important; border: none !important;
        height: 55px; width: 100% !important;
    }
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
# 4. LÓGICA DE VISTAS (COMPLETA)
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

# --- MODO REGISTRO ---
if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE NUEVO SOCIO</h1>", unsafe_allow_html=True)
    with st.form("form_reg_externo", clear_on_submit=True):
        rn = st.text_input("Nombre de la Tienda")
        rm = st.text_input("Email del Propietario")
        rt = st.text_input("WhatsApp (Ej: 58412...)")
        opciones_plan = {"GRATUITO": "🎁 GRATUITO ($0)", "BRONCE": "🥉 BRONCE ($5)", "PLATA": "🥈 PLATA ($15)", "ORO": "🥇 ORO ($30)"}
        plan_label = st.selectbox("Selecciona tu Plan", options=list(opciones_plan.values()))
        plan_sel = [k for k, v in opciones_plan.items() if v == plan_label][0]
        ri = st.file_uploader("Foto de Portada", type=['jpg', 'png'])
        ref_socio = st.text_input("Referencia de Pago")

        if st.form_submit_button("REGISTRAR COMERCIO"):
            if rn and rm and rt and ri and ref_socio:
                path_i = f"portadas/reg_{random.randint(1000,9999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path_i, ri.getvalue())
                url_i = supabase.storage.from_("fotos_productos").get_public_url(path_i)
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": rn, "email_propietario": rm.lower(), "whatsapp": rt, 
                    "portada_url": url_i, "plan": plan_sel, "codigo_acceso": "LUXURY7"
                }).execute()
                st.success("¡Registro Exitoso!")
                st.link_button("📲 NOTIFICAR AL ADMIN", f"https://wa.me/584241234567?text=Nueva Tienda: {rn} - Ref: {ref_socio}")

# --- MODO USUARIO (MALL Y TIENDA) ---
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
                        st.markdown(f'<img src="{t["portada_url"]}" class="img-portada-full">', unsafe_allow_html=True)
                        if st.button(t['nombre_comercio'].upper(), key=f"m_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        for p in prods:
            # Layout TikTok Inmersivo
            st.markdown(f"""
                <div class="video-wrapper">
                    <div class="overlay-price">${p['precio']}</div>
                    <div class="overlay-name">{p['nombre_producto']}</div>
            """, unsafe_allow_html=True)
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"btn_{p['id']}"):
                ventana_pago(p, t)
            st.markdown("<br><br>", unsafe_allow_html=True)

# --- MODO ADMIN (CONFIGURACIÓN) ---
else:
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
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        if res.data:
            perf = res.data[0]
            t1, t2, t3 = st.tabs(["➕ PRODUCTO", "🖼️ PORTADA", "💳 COBROS"])
            
            with t1:
                c_res = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                actual = c_res.count if c_res.count is not None else 0
                limite = PLANES.get(perf.get('plan', 'GRATUITO'), 3)
                st.write(f"Plan: {perf['plan']} ({actual}/{limite})")
                if actual < limite:
                    with st.form("add_p"):
                        n_p = st.text_input("Nombre")
                        p_p = st.number_input("Precio", min_value=0.0)
                        v_p = st.file_uploader("Video (MP4)", type=['mp4'])
                        if st.form_submit_button("PUBLICAR"):
                            path = f"v/{random.randint(1000,9999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(path, v_p.getvalue())
                            url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                            supabase.table("productos").insert({"nombre_producto":n_p, "precio":p_p, "video_url":url_v, "comercio_relacionado":perf['nombre_comercio']}).execute()
                            st.success("¡Listo!"); st.rerun()
            
            with t2:
                st.image(perf['portada_url'], width=150)
                nueva_f = st.file_uploader("Cambiar Logo", type=['jpg', 'png'])
                if st.button("GUARDAR LOGO"):
                    path = f"portadas/p_{perf['id']}.jpg"
                    supabase.storage.from_("fotos_productos").upload(path, nueva_f.getvalue(), {"x-upsert": "true"})
                    url_i = supabase.storage.from_("fotos_productos").get_public_url(path)
                    supabase.table("perfiles_comercio").update({"portada_url": url_i}).eq("id", perf['id']).execute()
                    st.success("Logo actualizado"); st.rerun()

            with t3:
                d_p = st.text_area("Datos de Pago", value=perf.get('datos_pago','') or "")
                if st.button("ACTUALIZAR DATOS"):
                    supabase.table("perfiles_comercio").update({"datos_pago": d_p}).eq("id", perf['id']).execute()
                    st.success("Guardado")

            if st.button("🚪 CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()