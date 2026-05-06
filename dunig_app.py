import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import string

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

PLANES_LIMITES = {"BRONCE": 0, "PLATINUM": 15, "DIAMANTE": 50}

def generar_codigo_fijo():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# --- CSS LUXURY ---
st.markdown("<style>.main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: white; } .stButton>button { background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295); color: black; border-radius: 30px; font-weight: 800; border: none; } .luxury-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(212,175,55,0.2); border-radius: 20px; padding: 20px; }</style>", unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA DE NAVEGACIÓN
# ==========================================
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if not es_admin:
    # --- VISTA MALL PÚBLICO (FILTRADO POR PAGO) ---
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        res = supabase.table("perfiles_comercio").select("*").neq("plan", "BRONCE").execute()
        tiendas = res.data
        
        if not tiendas:
            st.info("Próximamente más tiendas exclusivas disponibles.")
        else:
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
        st.button("⬅️ VOLVER", on_click=ir_a, args=('mall',))
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        for p in prods.data:
            st.video(p['video_url'])
            st.divider()

# ==========================================
# 3. PANEL DE CONTROL (CÓDIGO PERSISTENTE)
# ==========================================
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL LUXURY</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.form("login_f"):
            mail = st.text_input("Email Registrado")
            cod_acceso = st.text_input("Tu Código Luxury (7 dígitos)", type="password").upper()
            if st.form_submit_button("INGRESAR AL SISTEMA"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", mail).execute()
                if res.data:
                    user = res.data[0]
                    # Si no tiene código, se le asigna uno para siempre
                    if not user.get('codigo_acceso'):
                        nuevo_c = generar_codigo_fijo()
                        supabase.table("perfiles_comercio").update({"codigo_acceso": nuevo_c}).eq("id", user['id']).execute()
                        st.warning(f"Tu nuevo código permanente es: {nuevo_c}. Guárdalo bien.")
                    elif user.get('codigo_acceso') == cod_acceso:
                        st.session_state.logged_in = True
                        st.session_state.user_data = user
                        st.rerun()
                    else: st.error("Código incorrecto.")
                else: st.error("Email no encontrado.")
    else:
        perf = st.session_state.user_data
        plan = perf.get('plan', 'BRONCE').upper()
        
        if plan == "BRONCE":
            st.warning("⚠️ TU TIENDA ESTÁ OCULTA EN EL MALL. Activa un plan para ser visible al público.")
        
        t1, t2, t3, t4 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS", "💎 MI PLAN"])
        
        with t4:
            st.markdown("### 🏆 Membresía Luxury")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 👑 PLATINUM ($9.99)")
                with st.expander("Pagar"): st.write("Zelle: pagos@luxury.com")
            with c2:
                st.markdown("#### 💎 DIAMANTE ($29.99)")
                with st.expander("Pagar"): st.write("Zelle: vip@luxury.com")
            
            ref = st.text_input("Referencia de Pago")
            if st.button("ENVIAR AL GMAIL"):
                link = f"mailto:idealiting@gmail.com?subject=PAGO_{perf['nombre_comercio']}&body=Ref:{ref}"
                st.link_button("📩 REPORTAR", link)
