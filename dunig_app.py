import streamlit as st
from supabase import create_client, Client
import random
import string
import urllib.parse

# ==========================================
# 1. CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

def generar_codigo_fijo():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

# --- ESTÉTICA ---
st.markdown("<style>.main { background: #000; color: white; } .stButton>button { background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295); color: black !important; border-radius: 30px; font-weight: 800; border: none; width: 100%; }</style>", unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA DE ACCESO PERSONAL
# ==========================================
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    
    if not st.session_state.get('logged_in', False):
        st.markdown("<div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px;'>", unsafe_allow_html=True)
        
        email_log = st.text_input("Email del Negocio").lower().strip()
        pass_log = st.text_input("Código de Acceso", type="password").upper().strip()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔓 ENTRAR AL PANEL"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_log).execute()
                if res.data and res.data[0].get('codigo_acceso') == pass_log:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email_log
                    st.rerun()
                else:
                    st.error("Código o Email incorrecto.")

        with col2:
            if st.button("🔑 SOLICITAR MI CÓDIGO"):
                if email_log:
                    res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_log).execute()
                    if res.data:
                        user = res.data[0]
                        cod = user.get('codigo_acceso')
                        
                        # Si no existe código, lo creamos
                        if not cod:
                            cod = generar_codigo_fijo()
                            supabase.table("perfiles_comercio").update({"codigo_acceso": cod}).eq("id", user['id']).execute()
                        
                        # Preparamos el mensaje de WhatsApp
                        # Usamos el número guardado en la base de datos (asegúrate de tener columna 'whatsapp')
                        telefono = user.get('whatsapp', '') 
                        mensaje = f"*D'UNIG LUXURY*\n\nHola, tu código de acceso permanente es: *{cod}*\n\nGuarda este mensaje para entrar a tu panel."
                        msg_encoded = urllib.parse.quote(mensaje)
                        
                        # Botón que abre WhatsApp directamente
                        st.info("Haz clic abajo para recibir tu código por WhatsApp:")
                        st.link_button("🟢 RECIBIR POR WHATSAPP", f"https://wa.me/{telefono}?text={msg_encoded}")
                    else:
                        st.error("Email no registrado.")
                else:
                    st.warning("Escribe tu email primero.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success(f"Bienvenido: {st.session_state.user_email}")
        if st.button("Cerrar Sesión"):
            st.session_state.logged_in = False
            st.rerun()
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    st.info("Tiendas activas pronto.")
