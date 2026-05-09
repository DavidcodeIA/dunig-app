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
def verificar_expiracion(perfil):
    if perfil.get('plan') == "GRATUITO":
        try:
            f_reg_raw = perfil.get('fecha_registro')
            fecha_reg = datetime.strptime(str(f_reg_raw), '%Y-%m-%d').date() if f_reg_raw else date.today()
            dias_transcurridos = (date.today() - fecha_reg).days
            if dias_transcurridos >= 7 and perfil.get('activo') == True:
                supabase.table("perfiles_comercio").update({"activo": False}).eq("id", perfil['id']).execute()
                return False
        except:
            return perfil.get('activo', False)
    return perfil.get('activo', False)

# Constantes e Interfaz
PLANES_LIMITES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}
OPCIONES_PLAN_VISUAL = {
    "GRATUITO": "⚪ GRATUITO (Prueba 7 Días - 3 Productos)",
    "BRONCE": "🥉 BRONCE (Emprendedor - 10 Productos)",
    "PLATA": "🥈 PLATA (Crecimiento - 25 Productos)",
    "ORO": "👑 ORO (Ilimitado - Ventas Premium)"
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'registered' not in st.session_state: st.session_state.registered = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS MEJORADO)
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
    .img-mall-luxury, .video-mall-luxury {
        width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 25px;
        border: 2px solid #D4AF37; box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.3);
    }
    .welcome-card {
        background: rgba(0,0,0,0.8); padding: 40px; border-radius: 25px;
        border: 2px solid #D4AF37; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================
es_admin_master = st.query_params.get("admin") == "true"
es_via_register = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO ---
if es_via_register:
    if st.session_state.registered:
        st.balloons()
        st.markdown("<div class='welcome-card'><h1 style='color: #D4AF37;'>BIENVENIDO SOCIO</h1><p>Recibirás tu código por WhatsApp pronto.</p></div>", unsafe_allow_html=True)
        st.link_button("🚀 IR AL LOGIN", "https://dunig-app-luxury-v2.streamlit.app/?admin=true", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO LUXURY</h1>", unsafe_allow_html=True)
        with st.form("form_reg"):
            r_nombre = st.text_input("Nombre de la Tienda")
            r_email = st.text_input("Email").lower().strip()
            r_whatsapp = st.text_input("WhatsApp")
            r_plan = st.selectbox("Plan", options=list(PLANES_LIMITES.keys()), format_func=lambda x: OPCIONES_PLAN_VISUAL[x])
            r_foto = st.file_uploader("Portada (Imagen o Video)", type=['jpg', 'png', 'jpeg', 'mp4'])
            r_ref = st.text_input("Referencia de Pago")
            
            if st.form_submit_button("REGISTRAR"):
                if r_nombre and r_email and r_foto:
                    try:
                        fname = f"portadas/{int(time.time())}_{r_foto.name}"
                        supabase.storage.from_("fotos_productos").upload(fname, r_foto.getvalue())
                        url_p = supabase.storage.from_("fotos_productos").get_public_url(fname)
                        
                        supabase.table("perfiles_comercio").insert({
                            "nombre_comercio": r_nombre, "email_propietario": r_email, 
                            "whatsapp": r_whatsapp, "portada_url": url_p, 
                            "plan": r_plan, "referencia_pago": r_ref,
                            "codigo_acceso": f"LUX{random.randint(100,999)}", 
                            "activo": False, "fecha_registro": str(date.today())
                        }).execute()
                        st.session_state.registered = True
                        st.rerun()
                    except Exception as e:
                        st.warning("El comercio ya existe o hay un error de conexión.")
                else: st.error("Faltan datos.")

# --- VISTA: MALL (CON CORRECCIÓN DE VIDEO) ---
elif not es_admin_master and st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    datos = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
    tiendas = [t for t in datos if verificar_expiracion(t)]
    
    if not tiendas: st.info("Próximamente...")
    else:
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    url = t.get("portada_url", "")
                    with cols[j]:
                        # Si es video, usamos HTML5 para que no se vea negro
                        if url.lower().endswith(('.mp4', '.mov', '.webm')):
                            st.markdown(f'<video autoplay loop muted playsinline class="video-mall-luxury"><source src="{url}" type="video/mp4"></video>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<img src="{url}" class="img-mall-luxury">', unsafe_allow_html=True)
                        
                        st.markdown(f"<p style='text-align:center; font-weight:bold;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                        if st.button("EXPLORAR", key=f"btn_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

# --- VISTA: TIENDA / VITRINA (CORRECCIÓN PANTALLA NEGRA) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
    
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    # Traer productos de la vitrina
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        with st.container(border=True):
            st.write(f"### {p['nombre_producto']}")
            v_url = p.get('video_url', '')
            
            if v_url:
                # El secreto para que no se vea negro: muted + playsinline
                st.markdown(f'''
                    <div style="border-radius: 15px; overflow: hidden; border: 1px solid #D4AF37;">
                        <video width="100%" autoplay loop muted playsinline>
                            <source src="{v_url}" type="video/mp4">
                        </video>
                    </div>
                ''', unsafe_allow_html=True)
            
            st.write(f"**Precio: ${p['precio']}**")
            st.button(f"PEDIR POR WHATSAPP", key=f"buy_{p['id']}")

# --- VISTA: PANEL SOCIO ---
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE SOCIO</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        l_email = st.text_input("Email").strip().lower()
        l_code = st.text_input("Código", type="password").upper()
        if st.button("INGRESAR"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", l_email).execute()
            if res.data and str(res.data[0].get('codigo_acceso')).upper() == l_code:
                st.session_state.logged_in, st.session_state.user_email = True, l_email
                st.rerun()
            else: st.error("Datos incorrectos.")
    else:
        st.success(f"Socio: {st.session_state.user_email}")
        if st.button("CERRAR SESIÓN"):
            st.session_state.logged_in = False
            st.rerun()