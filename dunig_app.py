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
        
        # Limpiamos espacios y estandarizamos a minúsculas/mayúsculas
        email_log = st.text_input("Email del Negocio").strip().lower()
        pass_log = st.text_input("Código de Acceso", type="password").strip().upper()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔓 ENTRAR AL PANEL"):
                if email_log and pass_log:
                    # Buscamos al usuario de forma limpia
                    res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_log).execute()
                    
                    if res.data:
                        user = res.data[0]
                        # Comparamos quitando cualquier espacio accidental de la base de datos
                        cod_db = str(user.get('codigo_acceso', '')).strip().upper()
                        
                        if cod_db == pass_log:
                            st.session_state.logged_in = True
                            st.session_state.user_email = email_log
                            st.success("Acceso concedido...")
                            st.rerun()
                        else:
                            st.error(f"El código '{pass_log}' no coincide con el registrado.")
                    else:
                        st.error("Email no encontrado en el sistema.")
                else:
                    st.warning("Escribe tus datos.")

        with col2:
            if st.button("🔑 SOLICITAR MI CÓDIGO"):
                if email_log:
                    res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_log).execute()
                    if res.data:
                        user = res.data[0]
                        cod = user.get('codigo_acceso')
                        
                        if not cod:
                            cod = generar_codigo_fijo()
                            supabase.table("perfiles_comercio").update({"codigo_acceso": cod}).eq("id", user['id']).execute()
                        
                        # WhatsApp con número de la DB o uno por defecto para pruebas
                        telefono = str(user.get('whatsapp', '')).replace("+", "").strip()
                        mensaje = f"*D'UNIG LUXURY*\n\nHola! Tu llave maestra es: *{cod}*\n\nÚsala para entrar a tu panel."
                        
                        st.info(f"Código listo para enviar al +{telefono}")
                        st.link_button("🟢 RECIBIR POR WHATSAPP", f"https://wa.me/{telefono}?text={urllib.parse.quote(mensaje)}")
                    else:
                        st.error("Este email no existe en la base de datos.")
                else:
                    st.warning("Escribe tu correo primero.")
        st.markdown("</div>", unsafe_allow_html=True)
