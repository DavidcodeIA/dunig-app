import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import string

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Configuración de límites por plan
PLANES = {"BRONCE": 5, "PLATINUM": 15, "DIAMANTE": 50}

# Función para generar código alfanumérico de 7 dígitos
def generar_codigo_luxury():
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choice(caracteres) for _ in range(7))

# Manejo de estados
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'auth_code' not in st.session_state: st.session_state.auth_code = None
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. VISTA PÚBLICA (D'UNIG LUXURY MALL)
# ==========================================
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if not es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    # Lógica del Mall abierta al público (sin restricciones)
    res = supabase.table("perfiles_comercio").select("*").execute()
    for t in res.data:
        with st.container():
            st.markdown(f"### {t['nombre_comercio'].upper()}")
            if st.button(f"VER CATÁLOGO", key=t['id']):
                st.session_state.tienda_actual = t
                ir_a('tienda')
            st.divider()

# ==========================================
# 3. PANEL DE CONTROL (RESTRINGIDO)
# ==========================================
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL LUXURY</h1>", unsafe_allow_html=True)

    if not st.session_state.logged_in:
        with st.form("registro_acceso"):
            st.subheader("🔑 Validación de Identidad")
            u_email = st.text_input("Tu Email Registrado")
            u_whatsapp = st.text_input("Tu WhatsApp (Ej: 58412...)")
            btn_generar = st.form_submit_button("GENERAR CÓDIGO DE 7 DÍGITOS")

            if btn_generar and u_email and u_whatsapp:
                nuevo_cod = generar_codigo_luxury()
                st.session_state.auth_code = nuevo_cod
                texto_wa = f"Tu código de acceso Luxury es: *{nuevo_cod}*"
                url_wa = f"https://wa.me/{u_whatsapp}?text={urllib.parse.quote(texto_wa)}"
                st.success("Código generado internamente.")
                st.link_button("📩 RECIBIR CÓDIGO POR WHATSAPP", url_wa)

        st.divider()
        cod_input = st.text_input("Introduce tu código de 7 dígitos", max_chars=7).upper()
        if st.button("DESBLOQUEAR PANEL"):
            if cod_input == st.session_state.auth_code:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Código inválido o expirado.")

    else:
        # --- PANEL YA AUTENTICADO ---
        mail_check = st.text_input("Ingresa tu email para cargar tus datos")
        if mail_check:
            res_p = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail_check).execute()
            if res_p.data:
                perf = res_p.data[0]
                t1, t2, t3, t4 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS", "💎 MI PLAN"])

                with t4:
                    st.markdown("### 🏆 Gestión de Suscripción")
                    
                    # CORRECCIÓN DE ICONOS: Corona para Platinum, Diamante para Diamante
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 👑 PLAN PLATINUM")
                        st.write("**Inversión: $29.99/mes**")
                        with st.expander("💳 Ver Métodos de Pago"):
                            st.write("📍 **Pago Móvil:** 0412-1234567 | V-12345678 | Banco")
                            st.write("📍 **Zelle:** pagos@luxury.com")
                            st.write("📍 **Nequi:** +57 300 0000000")
                    
                    with col2:
                        st.markdown("#### 💎 PLAN DIAMANTE")
                        st.write("**Inversión: $99.99/mes**")
                        with st.expander("💳 Ver Métodos de Pago"):
                            st.write("📍 **Pago Móvil:** 0412-1234567 | V-12345678 | Banco")
                            st.write("📍 **Zelle:** vip@luxury.com")
                            st.write("📍 **Nequi:** +57 300 1111111")
                    
                    st.divider()
                    st.markdown("#### 🔄 Reportar Nuevo Pago")
                    p_e = st.selectbox("Plan pagado", ["PLATINUM", "DIAMANTE"])
                    metodo = st.selectbox("Método usado", ["Pago Móvil", "Zelle", "Nequi"])
                    ref = st.text_input("Número de Referencia")
                    
                    if st.button("ENVIAR COMPROBANTE"):
                        if ref:
                            info = f"🚀 *NUEVO PAGO LUXURY*\n🏪 *Tienda:* {perf['nombre_comercio']}\n💎 *Plan:* {p_e}\n💰 *Método:* {metodo}\n🎫 *Ref:* {ref}"
                            # Reemplaza TU_NUMERO con tu número real de administrador
                            st.link_button("CONFIRMAR POR WHATSAPP", f"https://wa.me/584XXXXXXXXX?text={urllib.parse.quote(info)}")
            else:
                st.error("Email no encontrado en la base de datos.")
