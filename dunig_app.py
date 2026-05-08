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

def obtener_cuentas_admin():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "cuentas_activacion").execute()
        return res.data[0]['valor'] if res.data else "⚠️ Cuentas de activación no configuradas."
    except:
        return "❌ Error al conectar con los ajustes del sistema."

# Diccionario de planes con sus límites
PLANES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}

# Nombres visuales para el selector
OPCIONES_PLAN_VISUAL = {
    "GRATUITO": "⚪ GRATUITO (Básico - 3 Productos)",
    "BRONCE": "🥉 BRONCE (Emprendedor - 10 Productos)",
    "PLATA": "🥈 PLATA (Crecimiento - 25 Productos)",
    "ORO": "👑 ORO (Ilimitado - Ventas Premium)"
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS ACTUALIZADO)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    
    /* Botones Dorados */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; text-transform: uppercase;
        border: none !important;
    }

    /* Portadas Cuadradas con esquinas ovaladas */
    .img-cuadrada-luxury {
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        border-radius: 25px; /* Esquinas ovaladas */
        border: 2px solid #D4AF37;
        box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.3);
        transition: transform 0.3s;
    }
    .img-cuadrada-luxury:hover {
        transform: scale(1.02);
    }

    /* Burbuja de precio */
    .price-bubble {
        position: absolute; top: 15px; right: 15px;
        background: rgba(0, 0, 0, 0.85); color: #39FF14; 
        padding: 5px 15px; border-radius: 50px;
        font-weight: 900; border: 2px solid #39FF14; z-index: 10;
    }

    /* Estilo para los beneficios */
    .benefit-card {
        background: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #D4AF37;
        text-align: center;
        margin-bottom: 10px;
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
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("ENVIAR POR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else: st.error("Por favor, ingrese la referencia de pago")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE SOCIO</h1>", unsafe_allow_html=True)
    
    # --- BLOQUE DE BENEFICIOS ATRACTIVOS ---
    st.markdown("### 🏆 ELIGE TU NIVEL DE EXCLUSIVIDAD")
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.markdown("<div class='benefit-card'>⚪<br><b>GRATUITO</b><br><small>3 Productos<br>Vitrina Básica</small></div>", unsafe_allow_html=True)
    with b2:
        st.markdown("<div class='benefit-card'>🥉<br><b>BRONCE</b><br><small>10 Productos<br>Vitrina Pro</small></div>", unsafe_allow_html=True)
    with b3:
        st.markdown("<div class='benefit-card'>🥈<br><b>PLATA</b><br><small>25 Productos<br>Mall Prioridad</small></div>", unsafe_allow_html=True)
    with b4:
        st.markdown("<div class='benefit-card'>👑<br><b>ORO</b><br><small>ILIMITADO<br>Soporte VIP</small></div>", unsafe_allow_html=True)

    with st.expander("💳 CUENTAS PARA ACTIVACIÓN DE PLAN", expanded=False):
        st.markdown(obtener_cuentas_admin())

    with st.form("form_reg_externo", clear_on_submit=True):
        rn = st.text_input("🏷️ Nombre de la Tienda")
        rm = st.text_input("📧 Email del Propietario").lower()
        rt = st.text_input("📱 WhatsApp (Ej: 58412...)")
        
        plan_sel = st.selectbox(
            "💎 Plan de Membresía:", 
            options=list(PLANES.keys()),
            format_func=lambda x: OPCIONES_PLAN_VISUAL[x]
        )
        
        ri = st.file_uploader("📸 Foto de Portada (Formato Cuadrado Sugerido)", type=['jpg', 'png'])
        ref_socio = st.text_input("🎫 Referencia de Pago del Plan")

        if st.form_submit_button("🚀 REGISTRAR MI COMERCIO"):
            if rn and rm and rt and ri and ref_socio:
                path_i = f"portadas/reg_{random.randint(1000,9999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path_i, ri.getvalue())
                url_i = supabase.storage.from_("fotos_productos").get_public_url(path_i)
                
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": rn, "email_propietario": rm, "whatsapp": rt, 
                    "portada_url": url_i, "plan": plan_sel, "codigo_acceso": f"LUX{random.randint(10,99)}"
                }).execute()
                st.success("¡Registro Exitoso! El administrador activará tu tienda pronto.")
            else: st.error("Por favor, completa todos los campos.")

elif not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        
        tiendas = supabase.table("perfiles_comercio").select("*").execute().data
        
        # --- FILAS DE DOS EN DOS CON PORTADAS CUADRADAS ---
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.markdown(f'<img src="{t.get("portada_url")}" class="img-cuadrada-luxury">', unsafe_allow_html=True)
                        st.markdown(f"<p style='text-align:center; color:#D4AF37; font-weight:bold; margin-top:5px;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                        if st.button("VISITAR", key=f"m_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        for p in prods:
            with st.container():
                st.markdown(f"<div style='position: relative;'><div class='price-bubble'>${p['precio']}</div></div>", unsafe_allow_html=True)
                st.video(p['video_url'], autoplay=True, loop=True, muted=True, format="video/mp4")
                if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"btn_{p['id']}", use_container_width=True):
                    ventana_pago(p, t)

else: # PANEL ADMIN
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.container(border=True):
            m = st.text_input("Email").strip().lower()
            c = st.text_input("Código de Acceso", type="password").strip().upper()
            if st.button("🔓 ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == c:
                    st.session_state.logged_in = True; st.session_state.user_email = m; st.rerun()
                else: st.error("Acceso denegado")
    else:
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        
        count_res = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
        actual = count_res.count if count_res.count is not None else 0
        limite = PLANES.get(perf['plan'], 3)
        
        st.write(f"💎 Plan Actual: **{perf['plan']}**")
        st.progress(min(actual / limite, 1.0))
        st.caption(f"Capacidad: {actual} de {limite} productos utilizados.")

        t1, t2, t3 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 PAGOS"])
        
        with t1:
            if actual < limite:
                with st.form("add_p", clear_on_submit=True):
                    n_p = st.text_input("Nombre del Producto")
                    p_p = st.number_input("Precio ($)", min_value=0.0)
                    v_p = st.file_uploader("Video (MP4)", type=['mp4'])
                    if st.form_submit_button("✨ PUBLICAR PRODUCTO"):
                        if n_p and v_p:
                            fname = f"v/{random.randint(1000,9999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(fname, v_p.getvalue(), {"content-type": "video/mp4"})
                            v_url = supabase.storage.from_("fotos_productos").get_public_url(fname)
                            supabase.table("productos").insert({"nombre_producto":n_p, "precio":p_p, "video_url":v_url, "comercio_relacionado":perf['nombre_comercio']}).execute()
                            st.success("¡Producto en línea!"); st.rerun()
            else: st.warning("Límite de plan alcanzado. Sube de nivel para agregar más.")

        with t2:
            st.subheader("📦 Gestión de Inventario")
            items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            for it in items:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    c1.write(f"**{it['nombre_producto']}** (${it['precio']})")
                    if c2.button("🗑️", key=f"del_{it['id']}", use_container_width=True):
                        # Borrado directo (Asegúrate de tener RLS DELETE activo)
                        supabase.table("productos").delete().eq("id", it['id']).execute()
                        st.toast(f"Producto eliminado")
                        st.rerun()

        with t3:
            d_p = st.text_area("Instrucciones de pago para tus clientes", value=perf.get('datos_pago','') or "", help="Escribe aquí tu banco, pago móvil o Zelle.")
            if st.button("💾 GUARDAR CONFIGURACIÓN DE PAGO"):
                supabase.table("perfiles_comercio").update({"datos_pago": d_p}).eq("id", perf['id']).execute()
                st.success("Datos actualizados correctamente.")

        st.divider()
        if st.button("🚪 CERRAR SESIÓN"):
            st.session_state.logged_in = False; st.rerun()