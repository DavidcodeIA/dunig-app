import streamlit as st
from supabase import create_client, Client
import random

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ESTADOS ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None
if 'carrito' not in st.session_state: st.session_state.carrito = {}

def navegar(dest, com=None):
    st.session_state.pagina = dest
    if com: st.session_state.comercio_sel = com
    st.rerun()

# --- PÁGINA: INICIO ---
if st.session_state.pagina == "inicio":
    st.title("⚜️ D'UNIG PLATINUM")
    c1, c2 = st.columns(2)
    c1.button("🛒 ENTRAR COMO CLIENTE", use_container_width=True, on_click=navegar, args=("centro_comercial",))
    c2.button("🏢 ACCESO COMERCIOS", use_container_width=True, on_click=navegar, args=("login_comercio",))

# --- PÁGINA: PANEL DE CARGA Y PERFIL ---
elif st.session_state.pagina == "panel_carga":
    nombre_c = st.session_state.comercio_sesion
    st.header(f"⚙️ Panel de {nombre_c}")
    
    # 1. Bloque de Perfil (Alineado al borde del elif)
    with st.expander("🖼️ CONFIGURAR PERFIL (Logo, WhatsApp, Pago)"):
        logo = st.file_uploader("Subir Logo del Negocio", type=['jpg','png'])
        ws = st.text_input("WhatsApp (Ej: 584121234567)")
        pago = st.text_area("Datos de Pago (Cta Bancaria, Pago Móvil, etc)")
        
        if st.button("Guardar Perfil"):
            # (Aquí va tu lógica de guardado de perfil que ya tienes)
            pass

    # 2. Bloque de Formulario (DEBE estar a la misma altura que el expander)
    with st.form("carga_video", clear_on_submit=True):
        st.subheader("🎬 Cargar Nuevo Video-Producto")
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        p_vid = st.file_uploader("Video del Producto (Máx 10s)", type=['mp4'])
        
        # El botón de enviar debe estar DENTRO del form (un nivel más adentro)
        enviar_btn = st.form_submit_button("PUBLICAR PRODUCTO")
        
        if enviar_btn:
            if p_nom and p_vid:
                # (Aquí va tu lógica de subida a Supabase)
                st.success("¡Video cargado con éxito!")
            else:
                st.warning("Faltan datos obligatorios.")

    # 3. Botón de salir (Alineado al borde del elif)
    st.button("🔙 SALIR AL INICIO", on_click=navegar, args=("inicio",))

# --- PÁGINA: VITRINA PERSONAL (VIDEO-CARRETE) ---
elif st.session_state.pagina == "vitrina_personal":
    tienda = st.session_state.comercio_sel
    perfil = supabase.table("perfiles_comercio").select("*").eq("nombre_comercio", tienda).single().execute()
    
    # Encabezado con Logo
    col_l, col_t = st.columns([1,4])
    if perfil.data and perfil.data.get('logo_url'):
        col_l.image(perfil.data['logo_url'], width=80)
    col_t.title(f"Tienda: {tienda}")

    productos = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
    
    for p in productos.data:
        with st.container():
            st.video(p['video_url'])
            st.subheader(f"{p['nombre_producto']} - {p['precio']}$")
            
            # Carrito de Sumar/Restar
            id_p = str(p['id'])
            cant = st.session_state.carrito.get(id_p, 0)
            c1, c2, c3 = st.columns([1,1,4])
            if c1.button("➖", key=f"min_{id_p}"):
                st.session_state.carrito[id_p] = max(0, cant - 1)
                st.rerun()
            c2.write(f"**{cant}**")
            if c3.button("➕", key=f"plus_{id_p}"):
                st.session_state.carrito[id_p] = cant + 1
                st.rerun()
            st.divider()

    # Botón Flotante de Pago
    total = sum([p['precio'] * st.session_state.carrito.get(str(p['id']), 0) for p in productos.data])
    if total > 0:
        if st.button(f"💳 PAGAR TOTAL: {total}$", use_container_width=True):
            navegar("pago")
    
    st.button("🔙 VOLVER", on_click=navegar, args=("centro_comercial",))

# --- PÁGINA: PAGO Y WHATSAPP ---
elif st.session_state.pagina == "pago":
    tienda = st.session_state.comercio_sel
    perfil = supabase.table("perfiles_comercio").select("*").eq("nombre_comercio", tienda).single().execute()
    
    st.header("🏁 Finalizar Pedido")
    st.subheader("Datos de Pago del Comercio:")
    st.info(perfil.data.get('datos_pago', 'No hay datos registrados'))
    
    # Generar Ticket para WhatsApp
    ticket = f"*PEDIDO D'UNIG PLATINUM*%0A---%0ATienda: {tienda}%0A"
    res = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
    total = 0
    for p in res.data:
        cant = st.session_state.carrito.get(str(p['id']), 0)
        if cant > 0:
            sub = p['precio'] * cant
            total += sub
            ticket += f"- {p['nombre_producto']} (x{cant}): {sub}$%0A"
    
    ticket += f"---%0A*TOTAL A PAGAR: {total}$*"
    ws_num = perfil.data.get('whatsapp', '')
    
    if st.button("✅ ENVIAR COMPROBANTE POR WHATSAPP"):
        link = f"https://wa.me/{ws_num}?text={ticket}"
        st.markdown(f'<a href="{link}" target="_blank">Abrir WhatsApp para finalizar</a>', unsafe_allow_html=True)

    st.button("🔙 REGRESAR", on_click=navegar, args=("vitrina_personal", tienda))

# --- PÁGINA: LOGIN (Simplificado) ---
elif st.session_state.pagina == "login_comercio":
    nom = st.text_input("Nombre de tu Tienda")
    if st.button("Entrar"):
        st.session_state.comercio_sesion = nom
        navegar("panel_carga")
