import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import string

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN (D'UNIG LUXURY)
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Configuración de límites de productos
PLANES_LIMITES = {
    "BRONCE": 3,        # Límite inicial hasta que verifiques el pago
    "PLATINUM": 15,     # Plan de $9.99
    "DIAMANTE": 50      # Plan de $29.99
}

# Función para generar código alfanumérico de 7 caracteres
def generar_codigo_luxury():
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choice(caracteres) for _ in range(7))

# Manejo de estados de sesión
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'auth_code' not in st.session_state: st.session_state.auth_code = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        animation: shimmer 5s infinite linear !important;
        color: #000 !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        border: none !important;
    }

    .luxury-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE PANELES
# ==========================================
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

# --- VISTA PÚBLICA: D'UNIG LUXURY MALL ---
if not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        busqueda = st.text_input("🔍 Buscar tiendas exclusivas...")
        res = supabase.table("perfiles_comercio").select("*").execute()
        tiendas = [t for t in res.data if busqueda.lower() in t['nombre_comercio'].lower()]
        
        cols = st.columns(2)
        for idx, t in enumerate(tiendas):
            with cols[idx % 2]:
                st.markdown(f"<div class='luxury-card'><h3 style='text-align:center;'>{t['nombre_comercio'].upper()}</h3>", unsafe_allow_html=True)
                if st.button("VISITAR", key=f"t_{t['id']}", use_container_width=True):
                    st.session_state.tienda_actual = t
                    ir_a('tienda')
                st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        st.button("⬅️ VOLVER AL MALL", on_click=ir_a, args=('mall',))
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        for p in prods.data:
            st.video(p['video_url'])
            st.divider()

# --- VISTA RESTRINGIDA: PANEL DE CONTROL LUXURY ---
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL LUXURY</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.form("auth_form"):
            st.subheader("🔑 Acceso Propietario")
            mail = st.text_input("Email registrado")
            whatsapp = st.text_input("WhatsApp (Ej: 584120000000)")
            submit = st.form_submit_button("GENERAR CÓDIGO DE 7 DÍGITOS")
            
            if submit and mail and whatsapp:
                if not st.session_state.auth_code:
                    st.session_state.auth_code = generar_codigo_luxury()
                
                msj_wa = f"Tu código de acceso D'UNIG LUXURY es: *{st.session_state.auth_code}*"
                wa_url = f"https://wa.me/{whatsapp}?text={urllib.parse.quote(msj_wa)}"
                st.info("Haz clic en el botón de abajo para recibir tu código por WhatsApp:")
                st.link_button("📩 RECIBIR CÓDIGO", wa_url)

        st.divider()
        input_codigo = st.text_input("Introduce el código de 7 dígitos", type="default").upper()
        if st.button("INGRESAR AL PANEL"):
            if input_codigo == st.session_state.auth_code:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Código incorrecto")
    
    else:
        # PANEL DE CONTROL AUTENTICADO
        mail_auth = st.text_input("Confirma tu Email para cargar gestión")
        if mail_auth:
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail_auth).execute()
            if res.data:
                perf = res.data[0]
                plan_actual = perf.get('plan', 'BRONCE').upper()
                limite_productos = PLANES_LIMITES.get(plan_actual, 3)
                
                # Conteo de productos actuales
                res_c = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                total_p = res_c.count if res_c.count else 0

                st.markdown(f"<div class='luxury-card'><h3>Bienvenido, {perf['nombre_comercio']}</h3>", unsafe_allow_html=True)
                c_a, c_b = st.columns(2)
                c_a.metric("Plan Activo", plan_actual)
                c_b.metric("Inventario", f"{total_p} / {limite_productos}")
                st.progress(min(total_p / limite_productos, 1.0))
                st.markdown("</div>", unsafe_allow_html=True)

                t1, t2, t3, t4 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS", "💎 MI PLAN"])
                
                with t1:
                    if total_p >= limite_productos:
                        st.error(f"Has alcanzado el límite de {limite_productos} productos. Sube de plan en 'MI PLAN' para habilitar más cupos.")
                    else:
                        with st.form("add_p", clear_on_submit=True):
                            n = st.text_input("Nombre del Producto")
                            p = st.number_input("Precio ($)", min_value=0.0)
                            v = st.file_uploader("Video publicitario (MP4)", type=['mp4'])
                            if st.form_submit_button("🚀 PUBLICAR"):
                                if n and v:
                                    v_path = f"videos/{random.randint(1000,9999)}.mp4"
                                    supabase.storage.from_("fotos_productos").upload(v_path, v.getvalue())
                                    v_url = supabase.storage.from_("fotos_productos").get_public_url(v_path)
                                    supabase.table("productos").insert({
                                        "nombre_producto": n, "precio": p, "video_url": v_url, 
                                        "comercio_relacionado": perf['nombre_comercio']
                                    }).execute()
                                    st.rerun()

                with t2:
                    items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                    for i in items.data:
                        with st.expander(f"📝 {i['nombre_producto']} - ${i['precio']}"):
                            if st.button("ELIMINAR", key=f"del_{i['id']}"):
                                supabase.table("productos").delete().eq("id", i['id']).execute()
                                st.rerun()

                with t3:
                    st.write("#### 💳 Cómo te pagan tus clientes")
                    p_info = st.text_area("Datos de Pago Móvil / Zelle / Nequi", value=str(perf.get('datos_pago', '')))
                    if st.button("GUARDAR DATOS"):
                        supabase.table("perfiles_comercio").update({"datos_pago": p_info}).eq("id", perf['id']).execute()
                        st.success("Información guardada.")

with t4:
                    st.markdown("### 🏆 Membresía D'UNIG LUXURY")
                    col_p1, col_p2 = st.columns(2)
                    
                    with col_p1:
                        st.markdown("#### 👑 PLAN PLATINUM")
                        st.markdown("<h2 style='color:#D4AF37;'>$9.99 <small>/mes</small></h2>", unsafe_allow_html=True)
                        st.write("✅ Hasta 15 productos.")
                        with st.expander("💳 Ver Datos de Pago"):
                            st.write("📍 **Pago Móvil:** 0412-1234567 | V-12345678 | Banco")
                            st.write("📍 **Zelle:** pagos@luxury.com")
                            st.write("📍 **Nequi:** +57 300 0000000")
                    
                    with col_p2:
                        st.markdown("#### 💎 PLAN DIAMANTE")
                        st.markdown("<h2 style='color:#D4AF37;'>$29.99 <small>/mes</small></h2>", unsafe_allow_html=True)
                        st.write("✅ Hasta 50 productos.")
                        with st.expander("💳 Ver Datos de Pago"):
                            st.write("📍 **Pago Móvil:** 0412-1234567 | V-12345678 | Banco")
                            st.write("📍 **Zelle:** vip@luxury.com")
                            st.write("📍 **Nequi:** +57 300 1111111")

                    st.divider()
                    st.markdown("#### 📧 Reportar Pago vía Email Corporativo")
                    plan_rep = st.selectbox("Plan adquirido", ["PLATINUM ($9.99)", "DIAMANTE ($29.99)"])
                    metodo_rep = st.selectbox("Método de pago", ["Pago Móvil", "Zelle", "Nequi"])
                    ref_rep = st.text_input("Número de Referencia / Operación")

                    if ref_rep:
                        # Configuración del correo profesional
                        destinatario = "idealiting@gmail.com"
                        asunto = f"REPORTE DE PAGO - {perf['nombre_comercio'].upper()}"
                        cuerpo = (
                            f"Cordial saludo, equipo de D'UNIG LUXURY.\n\n"
                            f"Por medio del presente adjunto los detalles de mi pago para la activación del plan:\n\n"
                            f"🏪 Comercio: {perf['nombre_comercio']}\n"
                            f"💎 Plan Seleccionado: {plan_rep}\n"
                            f"💰 Método de Pago: {metodo_rep}\n"
                            f"🎫 Referencia: {ref_rep}\n\n"
                            f"Quedo a la espera de la verificación y actualización de mis cupos de inventario."
                        )
                        
                        # Codificación para URL mailto
                        mailto_link = f"mailto:{destinatario}?subject={urllib.parse.quote(asunto)}&body={urllib.parse.quote(cuerpo)}"
                        
                        st.link_button("📩 ENVIAR COMPROBANTE AL GMAIL", mailto_link, use_container_width=True)
                        st.caption("Al hacer clic, se redactará un correo formal hacia idealiting@gmail.com")
                    else:
                        st.warning("Ingrese la referencia para habilitar el envío del reporte.")
