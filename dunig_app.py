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

# Credenciales de Supabase
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- FUNCIÓN PARA ENVIAR EMAIL AUTOMÁTICO ---
def enviar_email_automatico(destinatario, nombre_tienda, codigo):
    # DATOS DEL EMISOR
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
        # Puerto 465 con SSL es más estable para Gmail
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False
# ==========================================
# 2. PANEL DE CONTROL (LÓGICA AUTOMÁTICA)
# ==========================================
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL LUXURY</h1>", unsafe_allow_html=True)
    
    if not st.session_state.get('logged_in', False):
        st.markdown("<div style='background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px;'>", unsafe_allow_html=True)
        
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
                else:
                    st.error("Credenciales inválidas.")

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
                        
                        # Aquí ocurre la magia: envío invisible
                        with st.spinner("Enviando código de forma segura..."):
                            if enviar_email_automatico(email_log, user['nombre_comercio'], cod):
                                st.success(f"El código ha sido enviado a {email_log}. Revisa tu bandeja de entrada o SPAM.")
                    else:
                        st.error("Email no encontrado.")
                else:
                    st.warning("Escribe tu correo primero.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success(f"Bienvenido: {st.session_state.user_email}")
        if st.button("Cerrar Sesión"):
            st.session_state.logged_in = False
            st.rerun()
