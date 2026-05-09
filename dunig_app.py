import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import time
from datetime import datetime, date

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

# --- LÓGICA DE NEGOCIO ---
def obtener_cuentas_admin():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "cuentas_activacion").execute()
        return res.data[0]['valor'] if res.data else "⚠️ Cuentas de activación no configuradas."
    except:
        return "❌ Error al conectar con los ajustes del sistema."

def verificar_expiracion(perfil):
    """Verifica si un plan gratuito ha superado los 7 días."""
    if perfil.get('plan') == "GRATUITO":
        try:
            # Asumimos que la columna 'fecha_registro' existe en tu SQL
            fecha_reg_str = str(perfil.get('fecha_registro', date.today()))
            fecha_reg = datetime.strptime(fecha_reg_str, '%Y-%m-%d').date()
            dias_transcurridos = (date.today() - fecha_reg).days
            
            if dias_transcurridos >= 7 and perfil.get('activo') == True:
                # Desactivar automáticamente en base de datos
                supabase.table("perfiles_comercio").update({"activo": False}).eq("id", perfil['id']).execute()
                return False
        except:
            return perfil.get('activo', False)
    return perfil.get('activo', False)

# Constantes
PLANES_LIMITES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}
OPCIONES_PLAN_VISUAL = {
    "GRATUITO": "⚪ GRATUITO (Básico - 7 Días de Prueba)",
    "BRONCE": "🥉 BRONCE (Emprendedor - 10 Productos)",
    "PLATA": "🥈 PLATA (Crecimiento - 25 Productos)",
    "ORO": "👑 ORO (Ilimitado - Ventas Premium)"
}

# Estado de la Sesión
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
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS Y NAVEGACIÓN
# ==========================================
es_admin_master = st.query_params.get("admin") == "true"
es_via_register = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO DE SOCIO ---
if es_via_register:
    if st.session_state.registered:
        st.balloons()
        st.markdown("""
            <div class='welcome-card'>
                <h1 style='color: #D4AF37; font-size: 2.2rem;'>BIENVENIDOS A D'UNIG LUXURY</h1>
                <p style='font-size: 1.2rem;'>En el transcurso del día se <b>activará tu plan</b> y recibirás tu código por WhatsApp.</p>
            </div>
            """, unsafe_allow_html=True)
        st.link_button("🚀 IR AL PANEL", "https://dunig-app-luxury-v2.streamlit.app/?admin=true", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE SOCIO</h1>", unsafe_allow_html=True)
        with st.form("form_registro_luxury"):
            r_nombre = st.text_input("Nombre de la Tienda")
            r_email = st.text_input("Email").lower().strip()
            r_whatsapp = st.text_input("WhatsApp")
            r_plan = st.selectbox("Plan", options=list(PLANES_LIMITES.keys()), format_func=lambda x: OPCIONES_PLAN_VISUAL[x])
            r_foto = st.file_uploader("Foto Portada", type=['jpg', 'png'])
            r_ref = st.text_input("Referencia de Pago")
            
            if st.form_submit_button("SOLICITAR REGISTRO"):
                if all([r_nombre, r_email, r_whatsapp, r_foto, r_ref]):
                    try:
                        path = f"portadas/{int(time.time())}_{r_foto.name}"
                        supabase.storage.from_("fotos_productos").upload(path, r_foto.getvalue())
                        url_p = supabase.storage.from_("fotos_productos").get_public_url(path)
                        
                        supabase.table("perfiles_comercio").insert({
                            "nombre_comercio": r_nombre, "email_propietario": r_email, 
                            "whatsapp": r_whatsapp, "portada_url": url_p, 
                            "plan": r_plan, "referencia_pago": r_ref,
                            "codigo_acceso": f"LUX{random.randint(10,99)}", "activo": False,
                            "fecha_registro": str(date.today())
                        }).execute()
                        st.session_state.registered = True
                        st.rerun()
                    except Exception as e:
                        if "23505" in str(e) or "already exists" in str(e):
                            st.warning(f"⚠️ El correo **{r_email}** o el nombre de tienda ya existen. Intenta con otro o ingresa a tu panel.")
                        else:
                            st.error(f"Error técnico: {e}")
                else:
                    st.error("Por favor, llena todos los campos.")

# --- VISTA: MALL ---
elif not es_admin_master:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        tiendas_raw = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
        
        # Filtrar tiendas que expiraron (7 días gratis)
        tiendas = [t for t in tiendas_raw if verificar_expiracion(t)]
        
        if not tiendas: st.info("Próximamente más tiendas de lujo...")
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.markdown(f'<img src="{t.get("portada_url", "")}" class="img-mall-luxury">', unsafe_allow_html=True)
                        if st.button(f"VISITAR {t['nombre_comercio'].upper()}", key=f"t_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

# --- VISTA: PANEL DE CONTROL ---
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.container(border=True):
            l_email = st.text_input("Email").strip().lower()
            l_pass = st.text_input("Código", type="password").strip().upper()
            if st.button("🔓 ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", l_email).execute()
                if res.data:
                    u = res.data[0]
                    if str(u.get('codigo_acceso')).upper() == l_pass:
                        if verificar_expiracion(u):
                            st.session_state.logged_in, st.session_state.user_email = True, l_email
                            st.rerun()
                        else:
                            st.error("🚫 Tu periodo de prueba de 7 días ha vencido. Contacta a soporte.")
                    else: st.error("Código incorrecto.")
                else: st.error("Usuario no encontrado.")
    else:
        # Lógica de panel (Carga de productos, etc - mantener lo que ya tenías aquí)
        st.write(f"Bienvenido socio: {st.session_state.user_email}")
        if st.button("CERRAR SESIÓN"):
            st.session_state.logged_in = False
            st.rerun()