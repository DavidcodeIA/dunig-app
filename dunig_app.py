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
    
    with st.expander("🖼️ CONFIGURAR PERFIL (Logo, WhatsApp, Pago)"):
        logo = st.file_uploader("Subir Logo del Negocio", type=['jpg','png'])
        ws = st.text_input("WhatsApp (Ej: 584121234567)")
        pago = st.text_area("Datos de Pago (Cta Bancaria, Pago Móvil, etc)")
if st.button("Guardar Perfil"):
            try:
                url_logo = None
                if logo:
                    # Limpiamos el nombre para el bucket
                    nom_limpio = nombre_c.replace(" ", "_")
                    path = f"logos/{nom_limpio}_{random.randint(100,999)}.jpg"
                    supabase.storage.from_("fotos_productos").upload(path, logo.getvalue())
                    url_logo = supabase.storage.from_("fotos_productos").get_public_url(path)
                
                # Solo enviamos datos si tienen contenido
                data_update = {
                    "nombre_comercio": nombre_c,
                    "whatsapp": ws if ws else "",
                    "datos_pago": pago if pago else ""
                }
                
                if url_logo:
                    data_update["logo_url"] = url_logo
                
                # Intentamos el UPSERT
                supabase.table("perfiles_comercio").upsert(data_update, on_conflict="nombre_comercio").execute()
                st.success("✅ Perfil de comercio actualizado correctamente")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar perfil: {e}")

    with st.form("carga_video"):
        st.subheader("🎬 Cargar Nuevo Video-Producto")
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        p_vid = st.file_uploader("Video del Producto (Máx 10s)", type=['mp4'])
        if st.form_submit_button("PUBLICAR"):
            if p_nom and p_vid:
                path_v = f"productos/vid_{random.randint(1000,9999)}.mp4"
                supabase.storage.from_("fotos_productos").upload(path_v, p_vid.getvalue())
                url_v = supabase.storage.from_("fotos_productos").get_public_url(path_v)
                supabase.table("productos").insert({
                    "nombre_producto": p_nom, "precio": p_pre, 
                    "video_url": url_v, "comercio_propietario": nombre_c
                }).execute()
                st.success("¡Video cargado!")

    st.button("🔙 SALIR", on_click=navegar, args=("inicio",))

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
