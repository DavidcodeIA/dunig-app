import streamlit as st
from supabase import create_client, Client
import random

# --- 1. CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", page_icon="⚜️")

# --- 2. CONEXIÓN DIRECTA ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- 3. GESTIÓN DE NAVEGACIÓN Y CARRITO ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None
if 'carrito' not in st.session_state: st.session_state.carrito = {}

def navegar(destino, com=None):
    st.session_state.pagina = destino
    if com: st.session_state.comercio_sel = com
    st.rerun()

# --- 4. ESTILOS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .card-tienda { border: 1px solid #D4AF37; padding: 15px; border-radius: 20px; background: #1A1C23; text-align: center; }
    .video-card { border-bottom: 2px solid #D4AF37; padding-bottom: 20px; margin-bottom: 20px; }
    .price-tag { color: #D4AF37; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# FLUJO DE PÁGINAS
# ==========================================

# --- PÁGINA: INICIO ---
if st.session_state.pagina == "inicio":
    st.markdown("<h1 style='text-align:center;'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 ENTRAR AL CENTRO COMERCIAL", use_container_width=True):
            navegar("centro_comercial")
    with col2:
        if st.button("🏢 PANEL DE PROPIETARIOS", use_container_width=True):
            navegar("login_comercio")

# --- PÁGINA: LOGIN COMERCIO ---
elif st.session_state.pagina == "login_comercio":
    st.subheader("🔑 Acceso Propietario")
    nom = st.text_input("Nombre de tu Negocio")
    if st.button("INGRESAR"):
        if nom:
            st.session_state.comercio_sesion = nom
            navegar("panel_carga")
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- PÁGINA: PANEL DE CARGA (PROPIETARIO) ---
elif st.session_state.pagina == "panel_carga":
    nombre_c = st.session_state.comercio_sesion
    st.title(f"⚙️ Gestión: {nombre_c}")
    
    # SECCIÓN PERFIL
    with st.expander("🖼️ CONFIGURAR PERFIL (Logo, WhatsApp, Pago)"):
        logo = st.file_uploader("Logo del Negocio", type=['jpg','png'])
        ws = st.text_input("WhatsApp (Ej: 584121234567)")
        pago = st.text_area("Datos de Pago")
if st.button("Guardar Perfil"):
            try:
                url_l = None
                if logo:
                    # Nombre de archivo limpio
                    nom_archivo = "".join(filter(str.isalnum, nombre_c))
                    path = f"logos/{nom_archivo}_{random.randint(100,999)}.jpg"
                    supabase.storage.from_("fotos_productos").upload(path, logo.getvalue())
                    url_l = supabase.storage.from_("fotos_productos").get_public_url(path)
                
                # Preparamos los datos
                data = {
                    "nombre_comercio": nombre_c.strip(),
                    "whatsapp": str(ws).strip() if ws else "",
                    "datos_pago": pago.strip() if pago else ""
                }
                
                # Solo agregamos el logo si se subió uno nuevo
                if url_l:
                    data["logo_url"] = url_l

                # Ejecutamos el UPSERT
                supabase.table("perfiles_comercio").upsert(
                    data, 
                    on_conflict="nombre_comercio"
                ).execute()
                
                st.success(f"✅ Perfil de '{nombre_c}' guardado.")
                st.rerun()
                
            except Exception as e:
                st.error(f"Error de base de datos: {e}")
    # SECCIÓN CARGA PRODUCTO
    with st.form("form_video", clear_on_submit=True):
        st.subheader("🎬 Nuevo Video-Producto")
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        p_vid = st.file_uploader("Video (Max 10s)", type=['mp4'])
        if st.form_submit_button("🚀 PUBLICAR"):
            if p_nom and p_vid:
                path_v = f"productos/vid_{random.randint(1000,9999)}.mp4"
                supabase.storage.from_("fotos_productos").upload(path_v, p_vid.getvalue())
                url_v = supabase.storage.from_("fotos_productos").get_public_url(path_v)
                supabase.table("productos").insert({
                    "nombre_producto": p_nom, "precio": p_pre, 
                    "video_url": url_v, "comercio_propietario": nombre_c
                }).execute()
                st.success("¡Publicado!")

    st.button("🏠 CERRAR SESIÓN", on_click=navegar, args=("inicio",))

# --- PÁGINA: CENTRO COMERCIAL ---
elif st.session_state.pagina == "centro_comercial":
    st.title("🏢 CENTRO COMERCIAL D'UNIG")
    try:
        # Buscamos comercios que tengan perfil
        tiendas = supabase.table("perfiles_comercio").select("*").execute()
        if tiendas.data:
            cols = st.columns(3)
            for i, t in enumerate(tiendas.data):
                with cols[i % 3]:
                    st.markdown(f"<div class='card-tienda'>", unsafe_allow_html=True)
                    if t.get('logo_url'): st.image(t['logo_url'], width=100)
                    st.subheader(t['nombre_comercio'])
                    if st.button(f"Entrar a {t['nombre_comercio']}", key=f"t_{i}"):
                        navegar("vitrina_personal", t['nombre_comercio'])
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No hay tiendas activas.")
    except Exception as e: st.error(f"Error: {e}")
    st.button("🔙 VOLVER AL INICIO", on_click=navegar, args=("inicio",))

# --- PÁGINA: VITRINA PERSONAL (TIKTOK STYLE) ---
elif st.session_state.pagina == "vitrina_personal":
    tienda_nom = st.session_state.comercio_sel
    st.title(f"🏪 {tienda_nom}")
    
    # Traer productos
    prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda_nom).execute()
    
    if prods.data:
        for p in prods.data:
            with st.container():
                st.markdown("<div class='video-card'>", unsafe_allow_html=True)
                st.video(p['video_url'])
                st.subheader(p['nombre_producto'])
                st.markdown(f"<p class='price-tag'>{p['precio']}$</p>", unsafe_allow_html=True)
                
                # SISTEMA DE CARRITO
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

        # TOTAL Y BOTÓN DE PAGO
        prods_dict = {str(item['id']): item for item in prods.data}
        total = sum(prods_dict[k]['precio'] * v for k, v in st.session_state.carrito.items() if k in prods_dict)
        
        if total > 0:
            if st.button(f"💳 PAGAR TOTAL: {total}$", use_container_width=True):
                navegar("pago")
    
    st.button("🔙 REGRESAR AL CENTRO", on_click=navegar, args=("centro_comercial",))

# --- PÁGINA: PAGO Y WHATSAPP ---
elif st.session_state.pagina == "pago":
    tienda_nom = st.session_state.comercio_sel
    perfil = supabase.table("perfiles_comercio").select("*").eq("nombre_comercio", tienda_nom).single().execute()
    
    st.header("🏁 Finalizar Compra")
    st.subheader("Métodos de Pago:")
    st.info(perfil.data.get('datos_pago', 'Consultar pago al WhatsApp'))
    
    # Generar Ticket
    ticket = f"*PEDIDO D'UNIG PLATINUM*%0A---%0A"
    prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda_nom).execute()
    total = 0
    for p in prods.data:
        cant = st.session_state.carrito.get(str(p['id']), 0)
        if cant > 0:
            ticket += f"- {p['nombre_producto']} (x{cant}): {p['precio']*cant}$%0A"
            total += p['precio']*cant
    ticket += f"---%0A*TOTAL: {total}$*"
    
    if st.button("✅ ENVIAR PEDIDO AL WHATSAPP"):
        ws = perfil.data.get('whatsapp', '')
        st.markdown(f'<a href="https://wa.me/{ws}?text={ticket}" target="_blank">Abrir WhatsApp del Comercio</a>', unsafe_allow_html=True)
    
    st.button("🔙 VOLVER A LA TIENDA", on_click=navegar, args=("vitrina_personal", tienda_nom))
