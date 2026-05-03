import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def enviar_correo_clave(destinatario, nombre_negocio, clave):
    # --- CONFIGURACIÓN DE TU CORREO (Usa Secrets de Streamlit) ---
    remitente = st.secrets["EMAIL_USER"]
    password = st.secrets["EMAIL_PASS"] # Esta es la clave de aplicación de 16 dígitos

    asunto = f"⚜️ Bienvenida a D'UNIG PLATINUM - {nombre_negocio}"
    
    cuerpo = f"""
    <html>
    <body style="background-color: #0E1117; color: white; font-family: sans-serif; padding: 20px;">
        <h1 style="color: #D4AF37;">¡Bienvenido al Nivel Platinum!</h1>
        <p>Hola <b>{nombre_negocio}</b>,</p>
        <p>Tu comercio ha sido registrado con éxito. Aquí tienes tu llave de acceso personalizada:</p>
        <div style="background-color: #1A1C23; border: 1px solid #D4AF37; padding: 20px; text-align: center; border-radius: 10px;">
            <h2 style="color: #D4AF37; letter-spacing: 5px;">{clave}</h2>
        </div>
        <p>Úsala para ingresar a tu panel y cargar tus productos en la vitrina al instante.</p>
        <p style="color: #D4AF37;"><i>"Guardar la excelencia como la niña de tus ojos."</i></p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.attach(MIMEText(cuerpo, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False
        return False
