import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ... dentro de la pestaña de Registro de Comercio ...
if st.button("REGISTRAR Y ENVIAR CLAVE A MI CORREO"):
    if em_reg and nom_com:
        try:
            clave = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            # Guardamos en la base de datos
            supabase.table("perfiles_comercios").insert({
                "email": em_reg, "nombre_comercio": nom_com, "clave_acceso": clave
            }).execute()
            
            # ENVIAMOS EL CORREO
            exito = enviar_correo_clave(em_reg, nom_com, clave)
            
            if exito:
                st.success(f"✅ ¡Gloria a Dios! Tu clave ha sido enviada a **{em_reg}**.")
            else:
                st.warning(f"Se registró el comercio, pero hubo un detalle con el envío. Tu clave es: {clave}")
        except:
            st.error("Este correo ya está registrado.")
    
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
