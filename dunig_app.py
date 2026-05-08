import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

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

# FUNCIÓN DE BLINDAJE: Carga tus cuentas desde la tabla 'ajustes_sistema'
def obtener_cuentas_admin():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "cuentas_activacion").execute()
        return res.data[0]['valor'] if res.data else "⚠️ Cuentas no configuradas en el panel."
    except:
        return "❌ Error de conexión al cargar cuentas."

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
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 30px !important;
        font-weight: 800 !important; text-transform: uppercase;
    }
    .img-redonda {
        width: 140px; height: 140px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 10px auto; display: block;
        box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.4);
    }
    .price-bubble {
        position: absolute; top: 10px; right: 10px;
        background: rgba(0, 0, 0, 0.9); color: #39FF14; 
        padding: 5px 15px; border-radius: 50px;
        font-weight: 900; border: 2px solid #39FF14; z-index: 10;
    }
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
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **DATOS DE PAGO:**\n{tienda.get('datos_pago', 'Consultar al vendedor')}")
    ref = st.text_input("Ingrese Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Producto:* {producto['nombre_producto']}\n🔢 *Cant:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").replace("应用", "").strip()
            st.link_button("ENVIAR POR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else: st.error("Por favor, ingrese la referencia de pago")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE NUEVO SOCIO</h1>", unsafe_allow_html=True)
    
    with st.expander("💳 VER CUENTAS BANCARIAS PARA ACTIVACIÓN", expanded=True):
        # BLINDAJE: Las cuentas vienen de la base de datos, no del código
        st.markdown(obtener_cuentas_admin())
        st.caption("Copia el número de referencia antes de llenar el formulario.")

    with st.form("form_reg_externo", clear_on_submit=True):
        rn = st.text_input("Nombre de la Tienda")
        rm = st.text_input("Email del Propietario")
        rt = st.text_input("WhatsApp (Ej: 58412...)")
        
        opciones_plan = {
            "GRATUITO": "🎁 GRATUITO - 3 Productos ($0)",
            "BRONCE": "🥉 BRONCE - 10 Productos ($5)",
            "PLATA": "🥈 PLATA - 25 Productos ($15)",
            "ORO": "🥇 ORO - Productos Ilimitados ($30)"
        }
        plan_label = st.selectbox("Selecciona tu Plan", options=list(opciones_plan.values()))
        plan_sel = [k for k, v in opciones_plan.items() if v == plan_label][0]
        
        ri = st.file_uploader("Foto de Portada", type=['jpg', 'png'])
        ref_socio = st.text_input("Referencia de Pago")

        if st.form_submit_button("REGISTRAR COMERCIO"):
            if rn and rm and rt and ri and ref_socio:
                path_i = f"portadas/reg_{random.randint(1000,9999)}.jpg"
                # Subida optimizada
                supabase.storage.from_("fotos_productos").upload(path_i, ri.getvalue(), {"content-type": "image/jpeg"})
                url_i = supabase.storage.from_("fotos_productos").get_public_url(path_i)
                
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": rn, "email_propietario": rm.lower(), 
                    "whatsapp": rt, "portada_url": url_i, "plan": plan_sel,
                    "codigo_acceso": f"LUX-{random.randint(100,999)}"
                }).execute()
                
                tu_telf = "584120000000" # TU WHATSAPP REAL AQUÍ
                msj_pago = f"🚀 *NUEVO SOCIO*\n🏪 Tienda: {rn}\n💎 Plan: {plan_sel}\n🎫 Ref: {ref_socio}"
                st.success("¡Registro Exitoso!")
                st.link_button("📲 ENVIAR COMPROBANTE AL ADMIN", f"https://wa.me/{tu_telf}?text={urllib.parse.quote(msj_pago)}")
            else: 
                st.error("Completa todos los campos.")

elif not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        res = supabase.table("perfiles_comercio").select("*").execute()
        tiendas = res.data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        url = t.get('portada_url') or "https://via.placeholder.com/150"
                        st.markdown(f'<img src="{url}" class="img-redonda">', unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; color:#D4AF37; font-weight:bold;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                        if st.button("VISITAR", key=f"m_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ MALL"): ir_a('mall')
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        for p in prods.data:
            with st.container():
                st.markdown(f"<div style='position: relative;'><div class='price-bubble'>${p['precio']}</div></div>", unsafe_allow_html=True)
                # FORMATO FORZADO MP4: Para que no salga pantalla negra en móviles
                st.video(p['video_url'], autoplay=True, loop=True, muted=True, format="video/mp4")
                st.markdown(f"<h3 style='text-align:center;'>{p['nombre_producto']}</h3>", unsafe_allow_html=True)
                if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"btn_{p['id']}", use_container_width=True):
                    ventana_pago(p, t)
                st.divider()

else: # PANEL ADMIN
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
            t1, t2, t3 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS"])
            
            with t1:
                c_res = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                actual = c_res.count if c_res.count is not None else 0
                limite = PLANES.get(perf.get('plan', 'GRATUITO'), 3)
                st.write(f"Plan: **{perf.get('plan', 'GRATUITO')}** ({actual}/{limite})")
                
                if actual < limite:
                    with st.form("form_add", clear_on_submit=True):
                        nom_p = st.text_input("Nombre del Producto")
                        pre_p = st.number_input("Precio ($)", min_value=0.0)
                        vid_p = st.file_uploader("Video MP4", type=['mp4'])
                        if st.form_submit_button("PUBLICAR"):
                            if nom_p and vid_p:
                                path = f"v/{random.randint(1000,9999)}.mp4"
                                # CLAVE: Indicamos el tipo de video en la subida
                                supabase.storage.from_("fotos_productos").upload(path, vid_p.getvalue(), {"content-type": "video/mp4"})
                                url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                                supabase.table("productos").insert({"nombre_producto":nom_p, "precio":pre_p, "video_url":url_v, "comercio_relacionado":perf['nombre_comercio']}).execute()
                                st.success("¡Publicado!"); st.rerun()
                else: st.warning("Límite de plan alcanzado.")

            with t3:
                d_p = st.text_area("Datos de Pago para tus clientes", value=perf.get('datos_pago','') or "")
                if st.button("GUARDAR COBROS"):
                    supabase.table("perfiles_comercio").update({"datos_pago": d_p}).eq("id", perf['id']).execute()
                    st.success("Guardado")

            if st.button("🚪 CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()