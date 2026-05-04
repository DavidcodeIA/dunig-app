import streamlit as st
from supabase import create_client, Client
import random

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", initial_sidebar_state="collapsed")

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("⚠️ Error de conexión: Revisa tus Secrets.")
    st.stop()

def navegar(destino, com=None):
    st.session_state.pagina = destino
    if com: st.session_state.comercio_sel = com
    st.rerun()

# Estados de sesión
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None
if 'carrito' not in st.session_state: st.session_state.carrito = {}

# ==========================================
# 2. ESTILOS LUXURY 3D
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1c23 0%, #0e1117 100%); }
    .title-luxury { font-family: serif; color: #D4AF37; text-align: center; font-size: 3rem; }
    .stButton>button {
        background: linear-gradient(145deg, #d4af37, #b8860b);
        color: white !important;
        border-radius: 10px;
        box-shadow: 0px 4px 0px #8b6d05;
        font-weight: bold;
        width: 100%;
    }
    .card-luxury {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #D4AF37;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    .total-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: #D4AF37;
        color: black;
        text-align: center;
        padding: 10px;
        font-weight: bold;
        z-index: 100;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE PÁGINAS
# ==========================================

# --- INICIO ---
if st.session_state.pagina == "inicio":
    st.markdown("<h1 class='title-luxury'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: st.button("🛒 ENTRAR COMO CLIENTE", on_click=navegar, args=("centro_comercial",))
    with col2: st.button("🏢 ACCESO PROPIETARIO", on_click=navegar, args=("login_comercio",))

# --- LOGIN ---
elif st.session_state.pagina == "login_comercio":
    st.subheader("🔑 Acceso Propietario")
    nom_login = st.text_input("Nombre de tu Negocio")
    if st.button("INGRESAR"):
        if nom_login:
            st.session_state.comercio_sesion = nom_login.strip()
            navegar("panel_carga")
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- PANEL DE GESTIÓN (CARGA, INVENTARIO, PERFIL) ---
elif st.session_state.pagina == "panel_carga":
    nombre_c = st.session_state.comercio_sesion
    st.title(f"⚙️ Gestión: {nombre_c}")
    
    t1, t2, t3 = st.tabs(["🚀 Cargar", "📦 Inventario", "🖼️ Perfil"])
    
    with t1:
        with st.form("carga_p"):
            p_nom = st.text_input("Producto")
            p_pre = st.number_input("Precio ($)", min_value=0.0)
            p_vid = st.file_uploader("Video", type=['mp4'])
            if st.form_submit_button("PUBLICAR"):
                if p_nom and p_vid:
                    n_l = "".join(e for e in p_nom if e.isalnum())
                    path = f"productos/{n_l}_{random.randint(1000,9999)}.mp4"
                    supabase.storage.from_("fotos_productos").upload(path, p_vid.getvalue())
                    url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                    supabase.table("productos").insert({"nombre_producto": p_nom, "precio": p_pre, "video_url": url_v, "comercio_propietario": nombre_c}).execute()
                    st.success("✅ Publicado")
                    st.rerun()

    with t2:
        prods = supabase.table("productos").select("*").eq("comercio_propietario", nombre_c).execute()
        for p in prods.data:
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{p['nombre_producto']}** ({p['precio']}$)")
            if c2.button("🗑️", key=f"del_{p['id']}"):
                supabase.table("productos").delete().eq("id", p['id']).execute()
                st.rerun()

    with t3:
        st.subheader("Configuración del Perfil")
        p_logo = st.file_uploader("Actualizar Logo", type=['jpg', 'png'])
        p_ws = st.text_input("WhatsApp (Ej: 584121234567)")
        p_info = st.text_area("Datos de Pago")
        if st.button("GUARDAR PERFIL"):
            u_logo = None
            if p_logo:
                path_l = f"logos/{nombre_c}.jpg"
                supabase.storage.from_("fotos_productos").upload(path_l, p_logo.getvalue(), {"upsert": "true"})
                u_logo = supabase.storage.from_("fotos_productos").get_public_url(path_l)
            data = {"nombre_comercio": nombre_c, "whatsapp": p_ws, "datos_pago": p_info}
            if u_logo: data["logo_url"] = u_logo
            supabase.table("perfiles_comercio").upsert(data, on_conflict="nombre_comercio").execute()
            st.success("✅ Perfil guardado")

    st.button("🔙 SALIR", on_click=navegar, args=("inicio",))

# --- CENTRO COMERCIAL ---
elif st.session_state.pagina == "centro_comercial":
    st.markdown("<h1 class='title-luxury'>🛒 CENTRO COMERCIAL</h1>", unsafe_allow_html=True)
    res = supabase.table("perfiles_comercio").select("*").execute()
    for c in res.data:
        with st.container():
            st.markdown(f"<div class='card-luxury'><h3>💎 {c['nombre_comercio']}</h3></div>", unsafe_allow_html=True)
            st.button(f"VISITAR", key=f"vis_{c['nombre_comercio']}", on_click=navegar, args=("vitrina_personal", c['nombre_comercio']))
    st.button("🔙 INICIO", on_click=navegar, args=("inicio",))

# --- VITRINA PERSONAL CON CARRITO EN TIEMPO REAL ---
elif st.session_state.pagina == "vitrina_personal":
    tienda = st.session_state.comercio_sel
    st.markdown(f"<h1 class='title-luxury'>{tienda}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
    
    total_acumulado = 0
    for p in prods.data:
        with st.container():
            st.video(p['video_url'])
            st.subheader(p['nombre_producto'])
            st.write(f"Precio: {p['precio']}$")
            
            # Lógica de Carrito
            id_p = str(p['id'])
            cant = st.session_state.carrito.get(id_p, 0)
            
            c1, c2, c3 = st.columns([1,1,1])
            if c1.button("➖", key=f"min_{id_p}"):
                if cant > 0: st.session_state.carrito[id_p] = cant - 1; st.rerun()
            c2.markdown(f"<h3 style='text-align:center;'>{cant}</h3>", unsafe_allow_html=True)
            if c3.button("➕", key=f"add_{id_p}"):
                st.session_state.carrito[id_p] = cant + 1; st.rerun()
            
            total_acumulado += cant * p['precio']
            st.write("---")

    # Barra de total fija
    if total_acumulado > 0:
        st.markdown(f"""<div class='total-bar'>TOTAL A PAGAR: {total_acumulado}$</div>""", unsafe_allow_html=True)
        st.button("🏁 FINALIZAR COMPRA Y PAGAR", use_container_width=True, on_click=navegar, args=("pago",))
    
    st.button("🔙 VOLVER AL CENTRO", on_click=navegar, args=("centro_comercial",))

# --- PAGO Y WHATSAPP ---
elif st.session_state.pagina == "pago":
    tienda = st.session_state.comercio_sel
    st.title("🏁 PROCESAR PAGO")
    
    perfil = supabase.table("perfiles_comercio").select("*").eq("nombre_comercio", tienda).single().execute()
    st.info(f"Pagar a: {tienda}\n\n{perfil.data['datos_pago']}")
    
    # Generar resumen
    resumen = f"🛍️ *NUEVO PEDIDO - D'UNIG*%0A"
    prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
    total = 0
    for p in prods.data:
        cant = st.session_state.carrito.get(str(p['id']), 0)
        if cant > 0:
            resumen += f"• {p['nombre_producto']} (x{cant}): {p['precio']*cant}$%0A"
            total += p['precio']*cant
    
    resumen += f"*TOTAL: {total}$*"
    link = f"https://wa.me/{perfil.data['whatsapp']}?text={resumen}"
    
    st.markdown(f"""<a href="{link}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold;">📲 ENVIAR PEDIDO POR WHATSAPP</button></a>""", unsafe_allow_html=True)
    
    if st.button("🔙 CANCELAR"):
        st.session_state.carrito = {}
        navegar("vitrina_personal", tienda)
