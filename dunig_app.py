import streamlit as st
from supabase import create_client, Client
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- FUNCIÓN DE ENVÍO AUTOMÁTICO (CORREGIDA) ---
def enviar_email_automatico(destinatario, nombre_tienda, codigo):
    remitente = "idealiting@gmail.com" 
    password = st.secrets["GMAIL_PASSWORD"]

    msg = MIMEMultipart()
    msg['From'] = f"D'UNIG LUXURY <{remitente}>"
    msg['To'] = destinatario
    msg['Subject'] = f"🔐 Código de Acceso - {nombre_tienda}"

    cuerpo = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #000; color: #fff; padding: 20px;">
        <h2 style="color: #D4AF37;">D'UNIG LUXURY</h2>
        <p>Has solicitado el acceso al Panel de Control para <b>{nombre_tienda}</b>.</p>
        <div style="background-color: #1a1a1a; border: 1px solid #D4AF37; padding: 15px; text-align: center; border-radius: 10px;">
            <span style="font-size: 24px; letter-spacing: 5px; color: #D4AF37;"><b>{codigo}</b></span>
        </div>
        <p style="font-size: 12px; color: #888;">Si no solicitaste este código, ignora este mensaje.</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(cuerpo, 'html'))

    try:
        # Puerto 465 con SSL es el más seguro para evitar bloqueos de Google
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False

# ==========================================
# 2. INTERFAZ Y LÓGICA
# ==========================================
st.markdown("<style>.main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: white; } .stButton>button { background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295); color: black !important; border-radius: 30px; font-weight: 800; border: none; width: 100%; }</style>", unsafe_allow_html=True)

query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL LUXURY</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        email_log = st.text_input("Email Registrado").lower().strip()
        pass_log = st.text_input("Código de Acceso", type="password").upper().strip()
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔓 ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_log).execute()
                if res.data and res.data[0].get('codigo_acceso') == pass_log:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email_log
                    st.rerun()
                else: st.error("Credenciales inválidas.")

        with c2:
            if st.button("📩 ENVIAR CÓDIGO AL GMAIL"):
                if email_log:
                    res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_log).execute()
                    if res.data:
                        user = res.data[0]
                        cod = user.get('codigo_acceso')
                        if not cod:
                            cod = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))
                            supabase.table("perfiles_comercio").update({"codigo_acceso": cod}).eq("id", user['id']).execute()
                        
                        if enviar_email_automatico(email_log, user['nombre_comercio'], cod):
                            st.success(f"Código enviado a {email_log}")
                    else: st.error("Email no registrado.")
                else: st.warning("Escribe tu correo.")
    else:
        st.success(f"Sesión activa: {st.session_state.user_email}")
        if st.button("Cerrar Sesión"):
            st.session_state.logged_in = False
            st.rerun()
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    st.info("Mall Privado - Solo tiendas activas.")
