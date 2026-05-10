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

# Límites de productos reales (Máximo 100 para Oro)
PLANES = {
    "GRATUITO": 3,
    "BRONCE": 10,
    "PLATA": 25,
    "ORO": 100
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY MEJORADA (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000000; color: #ffffff; }
    
    /* BOTÓN COMPRAR (DORADO) */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 50px !important; width: 100% !important;
    }

    /* BOTÓN REGRESAR (DELGADO Y SIN FONDO) */
    .btn-regresar button {
        background: transparent !important; color: #ffffff !important; 
        border: 1px solid rgba(255,255,255,0.3) !important;
        height: 30px !important; font-size: 0.75rem !important;
        margin-top: 5px !important;
    }

    .img-redonda {
        width: 140px; height: 140px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 10px auto; display: block;
    }
    
    .price-bubble {
        position: absolute; top: 15px; right: 15px;
        background: rgba(0, 0, 0, 0.8); color: #39FF14; 
        padding: 5px 15px; border-radius: 50px;
        font-weight: 900; border: 2px solid #39FF14; z-index: 10;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DEL CARRITO (EL CORAZÓN DE LA VENTA)
# ==========================================
@st.dialog("💎 PROCESAR COMPRA LUXURY")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    st.write(f"Vendido por: **{tienda['nombre_comercio']}**")
    
    col1, col2 = st.columns(2)
    with col1:
        cantidad = st.number_input("Cantidad", min_value=1, value=1)
    with col2:
        total = float(producto['precio']) * cantidad
        st.metric("TOTAL", f"${total:,.2f}")
    
    st.divider()
    st.markdown("### 💳 MÉTODOS DE PAGO")
    st.info(tienda.get('datos_pago', '⚠️ El vendedor aún no ha configurado sus datos de pago.'))
    
    ref = st.text_input("Referencia o Captura de Pago (ID)")
    
    if st.button("🚀 CONFIRMAR Y NOTIFICAR POR WHATSAPP"):
        if ref:
            mensaje = (
                f"✨ *NUEVO PEDIDO LUXURY*\n\n"
                f"📦 *Producto:* {producto['nombre_producto']}\n"
                f"🔢 *Cantidad:* {cantidad}\n"
                f"💰 *Total:* ${total:,.2f}\n"
                f"🎫 *Referencia:* {ref}\n\n"
                f"¡Hola! Acabo de realizar el pago. Quedo atento a la entrega."
            )
            tel = str(tienda['whatsapp']).strip().replace("+", "")
            url_wa = f"https://wa.me/{tel}?text={urllib.parse.quote(mensaje)}"
            st.link_button("ABRIR WHATSAPP PARA FINALIZAR", url_wa)
        else:
            st.error("Por favor, ingresa la referencia para validar tu compra.")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO ---
if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE SOCIO</h1>", unsafe_allow_html=True)
    with st.form("registro_socio"):
        rn = st.text_input("Nombre de la Tienda")
        rm = st.text_input("Email")
        rt = st.text_input("WhatsApp (Ej: 58412...)")
        
        opciones_plan = {
            "GRATUITO": "🎁 GRATUITO - 3 Productos ($0)",
            "BRONCE": "🥉 BRONCE - 10 Productos ($5)",
            "PLATA": "🥈 PLATA - 25 Productos ($15)",
            "ORO": "🥇 ORO - 100 Productos ($30)"
        }
        plan_sel = st.selectbox("Plan de Expansión", options=list(opciones_plan.keys()), format_func=lambda x: opciones_plan[x])
        
        ri = st.file_uploader("Foto de Portada", type=['jpg', 'png'])
        ref_pago = st.text_input("Referencia de Pago de Activación")
        
        if st.form_submit_button("SOLICITAR ACTIVACIÓN"):
            if rn and rm and rt and ri and ref_pago:
                # Lógica de guardado...
                st.success("¡Solicitud enviada! El administrador activará tu tienda pronto.")

# --- VISTA: PANEL DE CONTROL (ADMIN) ---
elif es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.container(border=True):
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
        t1, t2, t3 = st.tabs(["📦 PRODUCTOS", "🖼️ PORTADA", "💳 PAGOS"])
        
        with t1:
            # AGREGAR PRODUCTO
            c_res = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            actual = c_res.count if c_res.count else 0
            limite = PLANES.get(perf['plan'], 3)
            st.write(f"Cupos: {actual} / {limite}")
            
            if actual < limite:
                with st.expander("➕ PUBLICAR NUEVO VIDEO"):
                    with st.form("add_p", clear_on_submit=True):
                        np = st.text_input("Nombre")
                        pp = st.number_input("Precio ($)")
                        vp = st.file_uploader("Video MP4", type=['mp4'])
                        if st.form_submit_button("SUBIR"):
                            # Lógica de subida...
                            st.rerun()
            
            # GESTIÓN (BORRAR PRODUCTOS)
            st.subheader("Tu Inventario")
            prods_m = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            for mp in prods_m:
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"🎥 {mp['nombre_producto']} - ${mp['precio']}")
                if col_b.button("🗑️", key=f"del_{mp['id']}"):
                    supabase.table("productos").delete().eq("id", mp['id']).execute()
                    st.rerun()

        with t2:
            st.subheader("Cambiar Foto de Portada")
            if perf['portada_url']: st.image(perf['portada_url'], width=150)
            nueva_p = st.file_uploader("Nueva Portada", type=['jpg', 'png'])
            if st.button("ACTUALIZAR FOTO"):
                # Lógica de actualización...
                st.rerun()

        with t3:
            st.subheader("Tus Datos de Cobro")
            datos = st.text_area("Instrucciones (Zelle, Pago Móvil, etc.)", value=perf.get('datos_pago', ''))
            if st.button("GUARDAR DATOS"):
                supabase.table("perfiles_comercio").update({"datos_pago": datos}).eq("id", perf['id']).execute()
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
                    st.markdown(f"<p style='text-align:center; font-weight:bold;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                    if st.button("ENTRAR", key=f"btn_t_{t['id']}", use_container_width=True):
                        st.session_state.tienda_actual = t
                        ir_a('tienda')

# --- VISTA: TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    
    # Botón de regreso minimalista
    st.markdown('<div class="btn-regresar">', unsafe_allow_html=True)
    if st.button("⬅️ REGRESAR AL MALL"): ir_a('mall')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    for p in prods:
        with st.container():
            st.markdown(f"<div style='position: relative;'><div class='price-bubble'>${p['precio']}</div></div>", unsafe_allow_html=True)
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            st.markdown(f"<h3 style='text-align:center;'>{p['nombre_producto']}</h3>", unsafe_allow_html=True)
            
            if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"p_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.divider()