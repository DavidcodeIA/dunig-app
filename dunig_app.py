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

# Límites de inventario
PLANES_LIMITES = {"BRONCE": 3, "PLATINUM": 15, "DIAMANTE": 50}

def generar_codigo_fijo():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# --- ESTÉTICA ---
st.markdown("<style>.main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: white; } .stButton>button { background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295); color: black; border-radius: 30px; font-weight: 800; border: none; } .luxury-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(212,175,55,0.2); border-radius: 20px; padding: 20px; margin-bottom: 15px; }</style>", unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA DE NAVEGACIÓN
# ==========================================
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if not es_admin:
    # --- MALL PÚBLICO (Solo tiendas que han pagado) ---
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        # Filtramos: Solo aparecen si el plan NO es BRONCE
        res = supabase.table("perfiles_comercio").select("*").neq("plan", "BRONCE").execute()
        
        if not res.data:
            st.info("Catálogo exclusivo en preparación. Regresa pronto.")
        else:
            cols = st.columns(2)
            for idx, t in enumerate(res.data):
                with cols[idx % 2]:
                    st.markdown(f"<div class='luxury-card'><h3 style='text-align:center;'>{t['nombre_comercio'].upper()}</h3>", unsafe_allow_html=True)
                    if st.button("VER TIENDA", key=f"t_{t['id']}", use_container_width=True):
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

# ==========================================
# 3. PANEL DE CONTROL (RESTRINGIDO)
# ==========================================
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL LUXURY</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.form("login_luxury"):
            st.subheader("🔑 Acceso Propietario")
            email_input = st.text_input("Email Registrado").lower().strip()
            pass_input = st.text_input("Tu Código Luxury (7 caracteres)", type="password").upper().strip()
            acceder = st.form_submit_button("INGRESAR")

            if acceder:
                if email_input:
                    # Buscamos al usuario en Supabase
                    res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_input).execute()
                    if res.data:
                        user = res.data[0]
                        cod_db = user.get('codigo_acceso')

                        # Si no tiene código, le asignamos uno nuevo y lo guardamos
                        if not cod_db:
                            nuevo_c = generar_codigo_fijo()
                            supabase.table("perfiles_comercio").update({"codigo_acceso": nuevo_c}).eq("id", user['id']).execute()
                            st.success(f"Bienvenido. Tu código permanente es: **{nuevo_c}**")
                            st.info("Guárdalo, lo necesitarás para siempre.")
                        
                        # Si el código coincide
                        elif cod_db == pass_input:
                            st.session_state.logged_in = True
                            st.session_state.user_email = email_input
                            st.rerun()
                        else:
                            st.error("Código incorrecto.")
                    else:
                        st.error("Email no encontrado. Regístrate con la administración.")
                else:
                    st.warning("Ingresa tu correo.")

        # Opción para recuperar código vía WhatsApp
        with st.expander("¿Olvidaste tu código?"):
            wa_recupa = st.text_input("Tu WhatsApp registrado")
            if st.button("RECUPERAR VÍA WHATSAPP"):
                res_r = supabase.table("perfiles_comercio").select("codigo_acceso").eq("email_propietario", email_input).execute()
                if res_r.data and res_r.data[0]['codigo_acceso']:
                    c_rec = res_r.data[0]['codigo_acceso']
                    msg = f"Hola, mi código Luxury es: {c_rec}"
                    st.link_button("Recibir en WhatsApp", f"https://wa.me/{wa_recupa}?text={urllib.parse.quote(msg)}")

    else:
        # --- PANEL YA LOGUEADO ---
        res_p = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        perf = res_p.data[0]
        plan = perf.get('plan', 'BRONCE').upper()
        
        if plan == "BRONCE":
            st.warning("⚠️ TU TIENDA ESTÁ OCULTA EN EL MALL. Paga un plan para activarla.")
        
        t1, t2, t3, t4 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS", "💎 MI PLAN"])
        
        with t1:
            limite = PLANES_LIMITES.get(plan, 3)
            # (Aquí va tu código de subir productos...)
            st.info(f"Capacidad actual: {limite} productos.")

        with t4:
            st.markdown("### 🏆 Membresía Luxury")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 👑 PLATINUM ($9.99)")
                with st.expander("Métodos de Pago"): st.write("Pago Móvil: 0412... / Zelle")
            with c2:
                st.markdown("#### 💎 DIAMANTE ($29.99)")
                with st.expander("Métodos de Pago"): st.write("Pago Móvil: 0412... / Zelle")
            
            ref = st.text_input("Ref de Pago")
            if st.button("REPORTAR AL GMAIL"):
                link = f"mailto:idealiting@gmail.com?subject=PAGO_{perf['nombre_comercio']}&body=Referencia:{ref}"
                st.link_button("Enviar Reporte", link)
