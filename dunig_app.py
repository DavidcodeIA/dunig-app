import streamlit as st
from supabase import create_client, Client
import random

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")

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

# --- 4. ESTILOS CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .card-tienda { border: 1px solid #D4AF37; padding: 20px; border-radius: 20px; background: #1A1C23; text-align: center; }
    .price-tag { color: #D4AF37; font-size: 26px; font-weight: bold; }
    .video-container { border-bottom: 2px solid #333; padding-bottom: 30px; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# LÓGICA DE PÁGINAS
# ==========================================

# --- INICIO ---
if st.session_state.pagina == "inicio":
    st.markdown("<h1 style='text-align:center;'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.button("🛒 ENTRAR COMO CLIENTE", use_container_width=True, on_click=navegar, args=("centro_comercial",))
    with c2:
        st.button("🏢 ACCESO PROPIETARIOS", use_container_width=True, on_click=navegar, args=("login_comercio",))

# --- LOGIN ---
elif st.session_state.pagina == "login_comercio":
    st.subheader("🔑 Acceso Propietario")
    nom = st.text_input("Nombre de tu Negocio")
    if st.button("INGRESAR"):
        if nom:
            st.session_state.comercio_sesion = nom
            navegar("panel_carga")
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- PANEL PROPIETARIO ---
elif st.session_state.pagina == "panel_carga":
    nombre_c = st.session_state.comercio_sesion
    st.title(f"⚙️ Gestión: {nombre_c}")
    
    with st.expander("🖼️ CONFIGURAR PERFIL (Logo, WhatsApp, Pago)"):
        logo = st.file_uploader("Logo", type=['jpg','png'])
        ws = st.text_input("WhatsApp (Ejem: 584121234567)")
        pago = st.text_area("Datos de Pago")
        if st.button("Guardar Perfil"):
            try:
                url_l = None
                if logo:
                    path = f"logos/{nombre_c}_{random.randint(100,999)}.jpg"
                    supabase.storage.from_("fotos_productos").upload(path, logo.getvalue())
                    url_l = supabase.storage.from_("fotos_productos").get_public_url(path)
                data = {"nombre_comercio": nombre_c, "whatsapp": ws, "datos_pago": pago}
                if url_l: data["logo_url"] = url_l
                supabase.table("perfiles_comercio").upsert(data, on_conflict="nombre_comercio").execute()
                st.success("✅ Perfil Guardado")
            except Exception as e: st.error(f"Error: {e}")

    with st.form("form_video", clear_on_submit=True):
        st.subheader("🎬 Nuevo Video-Producto (Máx 10s)")
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        p_vid = st.file_uploader("Video MP4", type=['mp4'])
        if st.form_submit_button("🚀 PUBLICAR"):
            if p_nom and p_vid:
                try:
                    path_v = f"productos/vid_{random.randint(1000,9999)}.mp4"
                    supabase.storage.from_("fotos_productos").upload(path_v, p_vid.getvalue())
                    url_v = supabase.storage.from_("fotos_productos").get_public_url(path_v)
                    supabase.table("productos").insert({
                        "nombre_producto": p_nom, "precio": p_pre, 
                        "video_url": url_v, "comercio_propietario": nombre_c
                    }).execute()
                    st.success("¡Video Publicado!")
                except Exception as e: st.error(f"Error: {e}")

    st.button("🏠 CERRAR SESIÓN", on_click=navegar, args=("inicio",))

# --- CENTRO COMERCIAL ---
elif st.session_state.pagina == "centro_comercial":
    st.title("🏢 CENTRO COMERCIAL D'UNIG")
    try:
        tiendas = supabase.table("perfiles_comercio").select("*").execute()
        if tiendas.data:
            cols = st.columns(3)
            for i, t in enumerate(tiendas.data):
                with cols[i % 3]:
                    st.markdown("<div class='card-tienda'>", unsafe_allow_html=True)
                    if t.get('logo_url'): st.image(t['logo_url'], width=100)
                    st.subheader(t['nombre_comercio'])
                    st.button("Entrar", key=f"btn_{t['id']}", on_click=navegar, args=("vitrina_personal", t['nombre_comercio']))
                    st.markdown("</div>", unsafe_allow_html=True)
        else: st.info("No hay tiendas activas.")
    except Exception as e: st.error(f"Error: {e}")
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- VITRINA PERSONAL ---
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
                    
                    pid = str(p['id'])
                    cant = st.session_state.carrito.get(pid, 0)
                    c1, c2, c3 = st.columns([1,1,4])
                    if c1.button("➖", key=f"minus_{pid}"):
                        st.session_state.carrito[pid] = max(0, cant - 1)
                        st.rerun()
                    c2.write(f"### {cant}")
                    if c3.button("➕", key=f"plus_{pid}"):
                        st.session_state.carrito[pid] = cant + 1
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            # Botón de Pago
            prods_dict = {str(item['id']): item for item in prods.data}
            total = sum(prods_dict[k]['precio'] * v for k, v in st.session_state.carrito.items() if k in prods_dict)
            if total > 0:
                if st.button(f"💳 PAGAR TOTAL: {total}$", use_container_width=True):
                    navegar("pago")
        else: st.warning("Esta tienda no tiene productos.")
    except Exception as e: st.error(f"Error: {e}")
    st.button("🔙 CENTRO COMERCIAL", on_click=navegar, args=("centro_comercial",))

# --- PAGO ---
elif st.session_state.pagina == "pago":
    tienda_nom = st.session_state.comercio_sel
    try:
        perfil = supabase.table("perfiles_comercio").select("*").eq("nombre_comercio", tienda_nom).single().execute()
        st.header("🏁 Finalizar Compra")
        st.info(f"Métodos de Pago de {tienda_nom}:\n{perfil.data.get('datos_pago', 'Consultar por WhatsApp')}")
        
        # Ticket
        ticket = f"*PEDIDO D'UNIG PLATINUM*%0A---%0A"
        prods_res = supabase.table("productos").select("*").eq("comercio_propietario", tienda_nom).execute()
        total_pago = 0
        for pr in prods_res.data:
            c_p = st.session_state.carrito.get(str(pr['id']), 0)
            if c_p > 0:
                ticket += f"- {pr['nombre_producto']} (x{c_p}): {pr['precio']*c_p}$%0A"
                total_pago += pr['precio']*c_p
        ticket += f"---%0A*TOTAL: {total_pago}$*"
        
        if st.button("✅ ENVIAR PEDIDO A WHATSAPP"):
            ws_num = perfil.data.get('whatsapp', '')
            st.markdown(f'<a href="https://wa.me/{ws_num}?text={ticket}" target="_blank">Abrir WhatsApp</a>', unsafe_allow_html=True)
    except Exception as e: st.error(f"Error en pago: {e}")
    st.button("🔙 VOLVER", on_click=navegar, args=("vitrina_personal", tienda_nom))
