import streamlit as st
from supabase import create_client, Client
import random

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", page_icon="⚜️")

# --- 2. CONEXIÓN ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- 3. ESTADOS Y NAVEGACIÓN ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None
if 'carrito' not in st.session_state: st.session_state.carrito = {}

def navegar(destino, com=None):
    st.session_state.pagina = destino
    if com: st.session_state.comercio_sel = com
    st.rerun()
# --- FUNCIÓN DE SEGURIDAD BIOMÉTRICA ---
def solicitar_huella():
    """Simula la petición de biometría al dispositivo"""
    st.markdown("---")
    st.markdown("### 🔒 Verificación de Identidad")
    st.info("Por favor, coloque su huella en el sensor del dispositivo para confirmar.")
    
    # En una App real, aquí llamaríamos a un componente JS (WebAuthn)
    # Por ahora, usamos un checkbox que simula el escaneo exitoso
    huella_detectada = st.checkbox("¿Huella reconocida correctamente?")
    
    if huella_detectada:
        st.success("✅ Identidad verificada. Acceso concedido.")
        return True
    return False
# --- 4. ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .card-tienda { border: 1px solid #D4AF37; padding: 20px; border-radius: 20px; background: #1A1C23; text-align: center; margin-bottom: 10px; }
    .price-tag { color: #D4AF37; font-size: 26px; font-weight: bold; }
    .video-container { border-bottom: 2px solid #333; padding-bottom: 30px; margin-bottom: 30px; border-radius: 15px; overflow: hidden; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# LÓGICA DE PÁGINAS
# ==========================================

# --- PÁGINA: INICIO ---
if st.session_state.pagina == "inicio":
    st.markdown("<h1 style='text-align:center;'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("🛒 ENTRAR AL CENTRO COMERCIAL", use_container_width=True, on_click=navegar, args=("centro_comercial",))
    with c2:
        st.button("🏢 ACCESO PROPIETARIOS", use_container_width=True, on_click=navegar, args=("login_comercio",))
# Debajo de los botones de Cliente y Propietario agrega este:
    st.button("🛵 SOCIO REPARTIDOR (DELIVERY)", use_container_width=True, on_click=navegar, args=("panel_delivery",))
# --- PÁGINA: LOGIN ---
elif st.session_state.pagina == "login_comercio":
    st.subheader("🔑 Acceso Propietario")
    nom_tienda = st.text_input("Nombre de tu Negocio")
    if st.button("INGRESAR AL PANEL"):
        if nom_tienda:
            st.session_state.comercio_sesion = nom_tienda
            navegar("panel_carga")
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- PÁGINA: PANEL DE CARGA (PROPIETARIO) ---
elif st.session_state.pagina == "panel_carga":
    nombre_c = st.session_state.comercio_sesion
    st.title(f"⚙️ Gestión: {nombre_c}")
    
    # 1. SECCIÓN PERFIL
    with st.expander("🖼️ CONFIGURAR MI VITRINA (Logo, WhatsApp, Pago)"):
        logo = st.file_uploader("Logo del Negocio", type=['jpg','png'])
        ws = st.text_input("WhatsApp (Ej: 584121234567)")
        pago = st.text_area("Datos para que el cliente te pague (Cuentas, Pago Móvil, etc.)")
        if st.button("Guardar Mi Perfil"):
            try:
                url_l = None
                if logo:
                    path = f"logos/{nombre_c}_{random.randint(100,999)}.jpg"
                    supabase.storage.from_("fotos_productos").upload(path, logo.getvalue())
                    url_l = supabase.storage.from_("fotos_productos").get_public_url(path)
                
                data = {
                    "nombre_comercio": nombre_c, 
                    "whatsapp": ws if ws else "", 
                    "datos_pago": pago if pago else ""
                }
                if url_l: data["logo_url"] = url_l
                
                supabase.table("perfiles_comercio").upsert(data, on_conflict="nombre_comercio").execute()
                st.success("✅ ¡Datos de vitrina actualizados!")
            except Exception as e:
                st.error(f"Error al guardar perfil: {e}")

    # 2. SECCIÓN CARGA PRODUCTO (CORREGIDA LA INDENTACIÓN)
    st.subheader("🎬 Cargar Nuevo Video-Producto")
    with st.form("form_carga_producto", clear_on_submit=True):
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        p_vid = st.file_uploader("Video (Máximo 10 segundos)", type=['mp4'])
        
        # El botón de submit DEBE estar aquí adentro
        btn_publicar = st.form_submit_button("🚀 PUBLICAR PRODUCTO")
        
        if btn_publicar:
            if p_nom and p_vid:
                try:
                    path_v = f"productos/vid_{random.randint(1000,9999)}.mp4"
                    supabase.storage.from_("fotos_productos").upload(path_v, p_vid.getvalue())
                    url_v = supabase.storage.from_("fotos_productos").get_public_url(path_v)
                    
                    supabase.table("productos").insert({
                        "nombre_producto": p_nom, 
                        "precio": p_pre, 
                        "video_url": url_v, 
                        "comercio_propietario": nombre_c
                    }).execute()
                    st.success("¡Video cargado con éxito!")
                except Exception as e:
                    st.error(f"Error al subir video: {e}")
            else:
                st.warning("Debes poner un nombre y subir un video.")

    st.button("🏠 CERRAR SESIÓN", on_click=navegar, args=("inicio",))

# --- PÁGINA: CENTRO COMERCIAL ---
elif st.session_state.pagina == "centro_comercial":
    st.title("🏢 CENTRO COMERCIAL D'UNIG")
    try:
        tiendas = supabase.table("perfiles_comercio").select("*").execute()
        if tiendas.data:
            cols = st.columns(3)
            for i, t in enumerate(tiendas.data):
                with cols[i % 3]:
                    st.markdown("<div class='card-tienda'>", unsafe_allow_html=True)
                    logo_url = t.get('logo_url')
                    if logo_url: st.image(logo_url, width=100)
                    else: st.markdown("<h1>🏪</h1>", unsafe_allow_html=True)
                    st.subheader(t['nombre_comercio'])
                    if st.button("Entrar", key=f"btn_store_{i}"):
                        navegar("vitrina_personal", t['nombre_comercio'])
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No hay tiendas activas todavía.")
    except Exception as e:
        st.error(f"Error al cargar tiendas: {e}")
    st.button("🔙 VOLVER AL INICIO", on_click=navegar, args=("inicio",))

# --- PÁGINA: VITRINA PERSONAL (VIDEO) ---
elif st.session_state.pagina == "vitrina_personal":
    tienda_nom = st.session_state.comercio_sel
    st.title(f"🏪 {tienda_nom}")
    
    try:
        prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda_nom).execute()
        if prods.data:
            for p in prods.data:
                with st.container():
                    st.markdown("<div class='video-container'>", unsafe_allow_html=True)
                    st.video(p['video_url'])
                    st.subheader(p['nombre_producto'])
                    st.markdown(f"<p class='price-tag'>{p['precio']}$</p>", unsafe_allow_html=True)
                    
                    # Carrito Suma/Resta
                    pid = str(p['id'])
                    cant = st.session_state.carrito.get(pid, 0)
                    c1, c2, c3 = st.columns([1,1,4])
                    if c1.button("➖", key=f"m_{pid}"):
                        st.session_state.carrito[pid] = max(0, cant - 1)
                        st.rerun()
                    c2.write(f"### {cant}")
                    if c3.button("➕", key=f"p_{pid}"):
                        st.session_state.carrito[pid] = cant + 1
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            # Cálculo de Total
            p_dict = {str(item['id']): item for item in prods.data}
            total = sum(p_dict[k]['precio'] * v for k, v in st.session_state.carrito.items() if k in p_dict)
            
            if total > 0:
                st.divider()
                if st.button(f"💳 FINALIZAR COMPRA: {total}$", use_container_width=True):
                    navegar("pago")
        else:
            st.warning("Esta tienda no tiene productos disponibles.")
    except Exception as e:
        st.error(f"Error al cargar productos: {e}")
    st.button("🔙 VOLVER AL CENTRO COMERCIAL", on_click=navegar, args=("centro_comercial",))

# --- PÁGINA: PAGO Y WHATSAPP ---
elif st.session_state.pagina == "pago":
    tienda_nom = st.session_state.comercio_sel
    st.header("🏁 Checkout y Pago")
    
    try:
        # Traer datos del comercio
        perfil = supabase.table("perfiles_comercio").select("*").eq("nombre_comercio", tienda_nom).single().execute()
        
        st.subheader("📌 Datos de Pago del Comercio")
        st.info(perfil.data.get('datos_pago', 'No se especificaron datos de pago.'))
        
        # Generar Factura/Ticket para WhatsApp
        ticket = f"*🎫 TICKET DE PEDIDO - D'UNIG PLATINUM*%0A"
        ticket += f"*Tienda:* {tienda_nom}%0A"
        ticket += f"----------------------------%0A"
        
        prods_res = supabase.table("productos").select("*").eq("comercio_propietario", tienda_nom).execute()
        total_final = 0
        
        for pr in prods_res.data:
            cantidad = st.session_state.carrito.get(str(pr['id']), 0)
            if cantidad > 0:
                subtotal = pr['precio'] * cantidad
                total_final += subtotal
                ticket += f"✅ {pr['nombre_producto']}%0A"
                ticket += f"   Cant: {cantidad} x {pr['precio']}$ = {subtotal}$%0A"
        
        ticket += f"----------------------------%0A"
        ticket += f"*TOTAL A PAGAR: {total_final}$*%0A%0A"
        ticket += f"Please enviarme el comprobante de pago por este medio."
        
        ws_num = perfil.data.get('whatsapp', '')
        
        if st.button("✅ ENVIAR TICKET Y COMPROBANTE AL WHATSAPP"):
            if ws_num:
                url_ws = f"https://wa.me/{ws_num}?text={ticket}"
                st.markdown(f'<a href="{url_ws}" target="_blank">📲 Presiona aquí para enviar el pedido</a>', unsafe_allow_html=True)
            else:
                st.error("El comercio no registró un número de WhatsApp.")
                
    except Exception as e:
        st.error(f"Error en el proceso de pago: {e}")
    
    st.button("🔙 VOLVER AL CARRITO", on_click=navegar, args=("vitrina_personal", tienda_nom)) 

# --- PÁGINA: PANEL DE DELIVERY ---
elif st.session_state.pagina == "panel_delivery":
    st.title("🛵 Panel de Repartidores")
    
    # Primero pedimos la huella para poder ver los pedidos
    if solicitar_huella():
        st.subheader("Pedidos listos para entregar")
        
        try:
            # Traemos productos que no han sido entregados
            pedidos = supabase.table("productos").select("*").execute()
            
            if pedidos.data:
                for p in pedidos.data:
                    with st.expander(f"📦 Pedido: {p['nombre_producto']}"):
                        st.write(f"Comercio: {p['comercio_propietario']}")
                        st.write(f"Monto a cobrar: {p['precio']}$")
                        
                        if st.button(f"CONFIRMAR ENTREGA Y COBRAR", key=f"deliv_{p['id']}"):
                            st.balloons()
                            st.success(f"¡Excelente! Pago de comisión activado para este reparto.")
            else:
                st.info("No hay pedidos pendientes en este momento.")
                
        except Exception as e:
            st.error(f"Error al cargar pedidos: {e}")
    else:
        st.warning("⚠️ Se requiere validación biométrica para gestionar entregas.")

    st.button("🔙 VOLVER AL INICIO", on_click=navegar, args=("inicio",))
