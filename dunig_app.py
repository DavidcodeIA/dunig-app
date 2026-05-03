import streamlit as st
from supabase import create_client, Client
import pandas as pd
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN DE PÁGINA LUXURY ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")

# --- FUNCIÓN: ENVIAR CORREO DE BIENVENIDA ---
def enviar_correo_clave(destinatario, nombre_negocio, clave):
    try:
        remitente = st.secrets["EMAIL_USER"]
        password = st.secrets["EMAIL_PASS"]
        
        asunto = f"⚜️ Tu Acceso Platinum a D'UNIG - {nombre_negocio}"
        cuerpo = f"""
        <html>
        <body style="background-color: #0E1117; color: white; font-family: sans-serif; padding: 20px;">
            <h1 style="color: #D4AF37; text-align: center;">⚜️ D'UNIG PLATINUM ⚜️</h1>
            <p>Hola <b>{nombre_negocio}</b>,</p>
            <p>Tu vitrina personalizada ha sido creada con éxito. Tu clave de acceso es:</p>
            <div style="background-color: #1A1C23; border: 2px solid #D4AF37; padding: 20px; text-align: center; border-radius: 15px;">
                <h2 style="color: #D4AF37; letter-spacing: 8px; font-size: 30px;">{clave}</h2>
            </div>
            <p style="text-align: center; color: #D4AF37; margin-top: 20px;"><i>"Excelencia en cada detalle."</i></p>
        </body>
        </html>
        """
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg.attach(MIMEText(cuerpo, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error técnico en el envío: {e}")
        return False

# --- CSS ANTIPUBLICIDAD Y DORADO ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0E1117; color: white; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    .card { border: 1px solid #D4AF37; padding: 20px; border-radius: 15px; background: #1A1C23; text-align: center; margin-bottom: 15px; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; border-radius: 12px; width: 100%; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN BASE DE DATOS ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ESTADOS ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'carrito' not in st.session_state: st.session_state.carrito = []
if 'user_auth' not in st.session_state: st.session_state.user_auth = None

def navegar(dest): 
    st.session_state.pagina = dest
    st.rerun()

# ==========================================
# 1. LANDING PAGE
# ==========================================
if st.session_state.pagina == "inicio":
    st.markdown("<h1>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='card'><h3>🛒 TIENDA</h3></div>", unsafe_allow_html=True)
        st.button("ENTRAR A COMPRAR", on_click=navegar, args=("cliente",))
    with c2:
        st.markdown("<div class='card'><h3>🏢 COMERCIOS</h3></div>", unsafe_allow_html=True)
        st.button("GESTIONAR MI VITRINA", on_click=navegar, args=("login_comercio",))
    
    st.markdown("<div class='card'><h3>🤝 AFILIADOS</h3></div>", unsafe_allow_html=True)
    st.button("PROGRAMA DE REFERIDOS", on_click=navegar, args=("afiliados",))

# ==========================================
# 2. SISTEMA COMERCIOS
# ==========================================
elif st.session_state.pagina == "login_comercio":
    st.markdown("<h2>🔑 ACCESO COMERCIANTE</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Ingresar", "Registrar Comercio"])
    
    with t2:
        em_reg = st.text_input("Correo para recibir clave")
        nom_com = st.text_input("Nombre de tu Negocio")
        if st.button("OBTENER CLAVE EN MI CORREO"):
            if em_reg and nom_com:
                clave = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                supabase.table("perfiles_comercios").insert({"email": em_reg, "nombre_comercio": nom_com, "clave_acceso": clave}).execute()
                if enviar_correo_clave(em_reg, nom_com, clave):
                    st.success(f"✅ ¡Gloria a Dios! Clave enviada a {em_reg}")
                else:
                    st.warning(f"Se registró pero el correo falló. Tu clave es: {clave}")

    with t1:
        em_in = st.text_input("Correo")
        pw_in = st.text_input("Clave", type="password")
        if st.button("ENTRAR AL PANEL"):
            res = supabase.table("perfiles_comercios").select("*").eq("email", em_in).eq("clave_acceso", pw_in).execute()
            if res.data:
                st.session_state.user_auth = res.data[0]
                navegar("panel_carga")
            else: st.error("Datos incorrectos.")
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

elif st.session_state.pagina == "panel_carga":
    nombre_t = st.session_state.user_auth['nombre_comercio']
    st.markdown(f"<h2>🏪 Vitrina Personal: {nombre_t}</h2>", unsafe_allow_html=True)
    
    with st.form("carga_p"):
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio $", min_value=0.0)
        p_img = st.text_input("Link Imagen")
        if st.form_submit_button("🚀 PUBLICAR AL INSTANTE"):
            supabase.table("productos").insert({"nombre_producto": p_nom, "precio": p_pre, "imagen_url": p_img, "comercio_propietario": nombre_t}).execute()
            st.toast("¡Producto cargado!")
    
    inv = supabase.table("productos").select("*").eq("comercio_propietario", nombre_t).execute()
    if inv.data: st.dataframe(pd.DataFrame(inv.data)[['nombre_producto', 'precio']])
    st.button("🏠 SALIR", on_click=navegar, args=("inicio",))

# ==========================================
# 3. AFILIADOS
# ==========================================
elif st.session_state.pagina == "afiliados":
    st.markdown("<h2>🤝 CONTROL DE AFILIADOS</h2>", unsafe_allow_html=True)
    with st.form("reg_af"):
        a_nom = st.text_input("Nombre Completo")
        a_em = st.text_input("Correo")
        if st.form_submit_button("REGISTRARME"):
            cod = f"DG-{random.randint(100,999)}"
            supabase.table("afiliados").insert({"nombre_afiliado": a_nom, "email_afiliado": a_em, "codigo_referido": cod}).execute()
            st.success(f"Tu código es: {cod}")

    if st.text_input("Auditoría (Clave)", type="password") == "afiliados2026":
        st.write("📋 Hoja de Control de Afiliados")
        data = supabase.table("afiliados").select("*").execute()
        if data.data: st.table(pd.DataFrame(data.data))
    st.button("🏠 VOLVER", on_click=navegar, args=("inicio",))

# ==========================================
# 4. VITRINA CLIENTE
# ==========================================
elif st.session_state.pagina == "cliente":
    st.markdown("<h1>🛍️ SHOPPING D'UNIG</h1>", unsafe_allow_html=True)
    # Lógica de vitrina, carrito, GPS y referencia bancaria...
    st.button("🏠 INICIO", on_click=navegar, args=("inicio",))
