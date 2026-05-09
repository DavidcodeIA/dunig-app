import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import time

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

@st.cache_resource 
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

supabase = init_connection()

def obtener_cuentas_admin():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "cuentas_activacion").execute()
        return res.data[0]['valor'] if res.data else "⚠️ Cuentas de activación no configuradas."
    except:
        return "❌ Error al conectar con los ajustes del sistema."

# Constantes del Sistema
PLANES_LIMITES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}
OPCIONES_PLAN_VISUAL = {
    "GRATUITO": "⚪ GRATUITO (Básico - 3 Productos)",
    "BRONCE": "🥉 BRONCE (Emprendedor - 10 Productos)",
    "PLATA": "🥈 PLATA (Crecimiento - 25 Productos)",
    "ORO": "👑 ORO (Ilimitado - Ventas Premium)"
}

# Gestión de Vistas y Estado de Sesión
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'registered' not in st.session_state: st.session_state.registered = False

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
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
    }
    .img-mall-luxury {
        width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 25px;
        border: 2px solid #D4AF37; box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.3); margin-bottom: 10px;
    }
    .welcome-card {
        background: rgba(0,0,0,0.7); padding: 30px; border-radius: 20px;
        border: 2px solid #D4AF37; text-align: center; margin-top: 20px;
    }
    .price-bubble {
        position: absolute; top: 15px; right: 15px;
        background: rgba(0, 0, 0, 0.85); color: #39FF14; 
        padding: 5px 15px; border-radius: 50px;
        font-weight: 900; border: 2px solid #39FF14; z-index: 10;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS Y FUNCIONES AUXILIARES
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
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("ENVIAR POR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else:
            st.error("Por favor, ingrese la referencia de pago")

@st.dialog("📝 EDITAR COMERCIO")
def editar_comercio_dialog(comercio):
    nuevo_whatsapp = st.text_input("WhatsApp", value=comercio.get('whatsapp', ''))
    nuevo_plan = st.selectbox("Plan", options=list(PLANES_LIMITES.keys()), index=list(PLANES_LIMITES.keys()).index(comercio.get('plan', 'GRATUITO')))
    nuevo_estado = st.toggle("Activo", value=comercio.get('activo', False))
    if st.button("GUARDAR"):
        supabase.table("perfiles_comercio").update({"whatsapp": nuevo_whatsapp, "plan": nuevo_plan, "activo": nuevo_estado}).eq("id", comercio['id']).execute()
        st.rerun()

# ==========================================
# 4. LÓGICA DE VISTAS (NAVEGACIÓN)
# ==========================================
es_admin_master = st.query_params.get("admin") == "true"
es_via_register = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO DE SOCIO ---
if es_via_register:
    if st.session_state.registered:
        st.balloons()
        st.markdown(f"""
            <div class='welcome-card'>
                <h1 style='color: #D4AF37; font-size: 2.2rem; line-height: 1.2;'>
                    BIENVENIDOS A D'UNIG LUXURY <br>
                    <span style='font-size: 1.5rem; color: #FFFFFF;'>tu mejor aliado comercial</span>
                </h1>
                <hr style='border: 0.5px solid #D4AF37; width: 60%; margin: 20px auto;'>
                <div style='padding: 0 10px; text-align: center;'>
                    <p style='font-size: 1.2rem; color: #f0f0f0;'>
                        En el transcurso del día se <b>activará tu plan</b> y se te entregará 
                        tu <b>código de ingreso</b> a través del número de WhatsApp que ingresaste.
                    </p>
                    <p style='color: #D4AF37; font-style: italic; margin-top: 15px;'>
                        ¡Es un honor tenerte con nosotros!
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.write("")
        st.link_button("🚀 IR AL PANEL DE CONTROL", "https://dunig-app-luxury-v2.streamlit.app/?admin=true", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE SOCIO</h1>", unsafe_allow_html=True)
        with st.expander("💳 CUENTAS PARA ACTIVACIÓN", expanded=False):
            st.markdown(obtener_cuentas_admin())

        with st.form("form_reg_externo"):
            r_nombre_tienda = st.text_input("Nombre de la Tienda")
            r_email = st.text_input("Email del Propietario").lower().strip()
            r_whatsapp = st.text_input("WhatsApp (Ej: 58412...)")
            plan_seleccionado = st.selectbox("Selecciona tu Plan", options=list(PLANES_LIMITES.keys()), format_func=lambda x: OPCIONES_PLAN_VISUAL[x])
            r_foto_portada = st.file_uploader("Foto de Portada", type=['jpg', 'png'])
            r_referencia_pago = st.text_input("Referencia de Pago")

            if st.form_submit_button("SOLICITAR REGISTRO"):
                if r_nombre_tienda and r_email and r_whatsapp and r_foto_portada and r_referencia_pago:
                    try:
                        path_portada = f"portadas/reg_{int(time.time())}_{r_foto_portada.name}"
                        supabase.storage.from_("fotos_productos").upload(path_portada, r_foto_portada.getvalue())
                        url_portada_final = supabase.storage.from_("fotos_productos").get_public_url(path_portada)
                        
                        supabase.table("perfiles_comercio").insert({
                            "nombre_comercio": r_nombre_tienda, "email_propietario": r_email, 
                            "whatsapp": r_whatsapp, "portada_url": url_portada_final, 
                            "plan": plan_seleccionado, "referencia_pago": r_referencia_pago,
                            "codigo_acceso": f"LUX{random.randint(10,99)}", "activo": False 
                        }).execute()
                        st.session_state.registered = True
                        st.rerun()
                    except Exception as e:
                        st.error("Error al registrar: Verifica las columnas en Supabase.")
                else:
                    st.error("Completa todos los campos.")

# --- VISTA: MALL / TIENDA ---
elif not es_admin_master:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
        if not tiendas: st.info("Próximamente más tiendas...")
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.markdown(f'<img src="{t.get("portada_url", "")}" class="img-mall-luxury">', unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; color:#D4AF37;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                        if st.button("VISITAR", key=f"mall_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER"): ir_a('mall')
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        for p in prods:
            st.markdown(f"<div style='position: relative;'><div class='price-bubble'>${p['precio']}</div></div>", unsafe_allow_html=True)
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"p_{p['id']}", use_container_width=True):
                ventana_pago(p, t)

# --- VISTA: PANEL DE CONTROL ---
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.container(border=True):
            l_email = st.text_input("Email").strip().lower()
            l_codigo = st.text_input("Código", type="password").strip().upper()
            if st.button("🔓 ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", l_email).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == l_codigo:
                    st.session_state.logged_in, st.session_state.user_email = True, l_email
                    st.rerun()
                else: st.error("Datos incorrectos.")
    else:
        perfil = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        res_count = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perfil['nombre_comercio']).execute()
        cant_actual = res_count.count or 0
        cant_limite = PLANES_LIMITES.get(perfil.get('plan', 'GRATUITO'), 3)
        
        st.write(f"Socio: **{perfil['nombre_comercio']}** | Plan: **{perfil.get('plan', 'GRATUITO')}**")
        st.progress(min(cant_actual / cant_limite, 1.0), text=f"Capacidad: {cant_actual}/{cant_limite}")

        t1, t2, t3, *t4 = st.tabs(["➕ PRODUCTO", "📦 CATÁLOGO", "⚙️ PERFIL"] + (["🏙️ MAESTRO"] if perfil['nombre_comercio'].upper() == "D'UNIG LUXURY" else []))
        
        with t1:
            if cant_actual < cant_limite:
                with st.form("add_p", clear_on_submit=True):
                    n = st.text_input("Nombre"); p = st.number_input("Precio"); v = st.file_uploader("Video", type=['mp4'])
                    if st.form_submit_button("🚀 PUBLICAR"):
                        fname = f"videos/{int(time.time())}.mp4"
                        supabase.storage.from_("fotos_productos").upload(fname, v.getvalue(), {"content-type": "video/mp4"})
                        url = supabase.storage.from_("fotos_productos").get_public_url(fname)
                        supabase.table("productos").insert({"nombre_producto": n, "precio": p, "video_url": url, "comercio_relacionado": perfil['nombre_comercio']}).execute()
                        st.rerun()
        with t2:
            for it in supabase.table("productos").select("*").eq("comercio_relacionado", perfil['nombre_comercio']).execute().data:
                c1, c2 = st.columns([4, 1])
                c1.write(f"{it['nombre_producto']} - ${it['precio']}")
                if c2.button("🗑️", key=f"del_{it['id']}"):
                    supabase.table("productos").delete().eq("id", it['id']).execute(); st.rerun()
        with t3:
            pagos = st.text_area("Datos de Pago", value=perfil.get('datos_pago', ''))
            if st.button("💾 GUARDAR"):
                supabase.table("perfiles_comercio").update({"datos_pago": pagos}).eq("id", perfil['id']).execute(); st.success("Guardado")
        
        if t4:
            with t4[0]:
                for c in supabase.table("perfiles_comercio").select("*").execute().data:
                    with st.container(border=True):
                        st.write(f"**{c['nombre_comercio']}** | Ref: {c.get('referencia_pago')}")
                        if st.button("📝", key=f"ed_{c['id']}"): editar_comercio_dialog(c)

        if st.button("🚪 CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()