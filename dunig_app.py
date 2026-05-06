import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import string

# ==========================================
# 1. CONEXIÓN Y CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

PLANES_LIMITES = {"BRONCE": 3, "PLATINUM": 15, "DIAMANTE": 50}

def generar_codigo_fijo():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

# --- ESTÉTICA ---
st.markdown("<style>.main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: white; } .stButton>button { background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295); color: black; border-radius: 30px; font-weight: 800; border: none; width: 100%; }</style>", unsafe_allow_html=True)

# ==========================================
# 2. PANEL DE CONTROL (REESTRUCTURADO)
# ==========================================
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL LUXURY</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        # Usamos columnas para un diseño más limpio
        with st.container():
            st.subheader("🔑 Acceso Propietario")
            email_input = st.text_input("Email Registrado", key="email_log").lower().strip()
            pass_input = st.text_input("Tu Código Luxury", type="password", key="pass_log").upper().strip()
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("INGRESAR"):
                    if email_input and pass_input:
                        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_input).execute()
                        if res.data:
                            user = res.data[0]
                            if user.get('codigo_acceso') == pass_input:
                                st.session_state.logged_in = True
                                st.session_state.user_email = email_input
                                st.success("Acceso concedido. Cargando...")
                                st.rerun()
                            else:
                                st.error("Código incorrecto.")
                        else:
                            st.error("Email no encontrado.")
                    else:
                        st.warning("Completa los datos.")

            with col_btn2:
                if st.button("SOLICITAR / CREAR CÓDIGO"):
                    if email_input:
                        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_input).execute()
                        if res.data:
                            user = res.data[0]
                            cod_existente = user.get('codigo_acceso')
                            
                            if not cod_existente:
                                nuevo_c = generar_codigo_fijo()
                                supabase.table("perfiles_comercio").update({"codigo_acceso": nuevo_c}).eq("id", user['id']).execute()
                                st.success(f"¡Código Creado! Tu llave es: **{nuevo_c}**")
                                st.info("Cópialo y úsalo en la casilla de arriba para ingresar.")
                            else:
                                st.info(f"Ya tienes un código asignado. Solicítalo a soporte si lo olvidaste.")
                        else:
                            st.error("Email no registrado en el sistema.")
                    else:
                        st.warning("Escribe tu email primero.")

    else:
        # --- PANEL DE GESTIÓN (DENTRO) ---
        res_p = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        if res_p.data:
            perf = res_p.data[0]
            plan = perf.get('plan', 'BRONCE').upper()
            
            if plan == "BRONCE":
                st.warning("⚠️ TIENDA OCULTA: Activa un plan en 'MI PLAN' para ser visible en el Mall.")
            
            tabs = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS", "💎 MI PLAN"])
            
            with tabs[3]: # Pestaña de Pagos
                st.markdown("### 🏆 Membresía Luxury")
                c1, c2 = st.columns(2)
                with c1: st.markdown("#### 👑 PLATINUM ($9.99)")
                with c2: st.markdown("#### 💎 DIAMANTE ($29.99)")
                
                ref = st.text_input("Número de Referencia")
                if st.button("REPORTAR PAGO AL GMAIL"):
                    if ref:
                        asunto = f"PAGO_{perf['nombre_comercio']}".replace(" ", "_")
                        cuerpo = f"Comercio: {perf['nombre_comercio']}%0AReferencia: {ref}"
                        mailto = f"mailto:idealiting@gmail.com?subject={asunto}&body={cuerpo}"
                        st.link_button("📩 ENVIAR A GMAIL", mailto)
        
        if st.button("SALIR DEL PANEL"):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.rerun()

else:
    # --- MALL PÚBLICO (FILTRADO) ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    res = supabase.table("perfiles_comercio").select("*").neq("plan", "BRONCE").execute()
    if res.data:
        for t in res.data:
            st.markdown(f"<div class='luxury-card'><h3>{t['nombre_comercio'].upper()}</h3></div>", unsafe_allow_html=True)
    else:
        st.info("Mall exclusivo. Próximamente nuevas tiendas.")
