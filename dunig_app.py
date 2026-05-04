import streamlit as st
from supabase import create_client, Client
import random

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN LUXURY
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

# Inicialización de estados
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None
if 'carrito' not in st.session_state: st.session_state.carrito = {}

# ==========================================
# 2. ESTILOS LUXURY 3D (CSS)
# ==========================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Poppins:wght@300;400;600&display=swap');
    .main { background: radial-gradient(circle, #1a1c23 0%, #0e1117 100%); }
    .title-luxury { font-family: 'Playfair Display', serif; color: #D4AF37; text-align: center; font-size: 3rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    .stButton>button {
        background: linear-gradient(145deg, #d4af37, #b8860b);
        color: white !important;
        border: none;
        padding: 12px 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 0px #8b6d05, 0px 8px 12px rgba(0,0,0,0.4);
        font-weight: 600;
        width: 100%;
        text-transform: uppercase;
    }
    .card-luxury {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(212, 175, 55, 0.3);
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 15px;
    }
    .total-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(90deg, #d4af37, #b8860b);
        color: black;
        text-align: center;
        padding: 15px;
        font-weight: 900;
        font-size: 20px;
        z-index: 1000;
        box-shadow: 0px -5px 15px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE PÁGINAS
# ==========================================

# --- INICIO ---
if st.session_state.pagina == "inicio":
    st.markdown("<h1 class='title-luxury'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns(2)
    with col1: st.button("🛒 ENTRAR COMO CLIENTE", on_click=navegar, args=("centro_comercial",))
    with col2: st.button("🏢 ACCESO PROPIETARIO", on_click=navegar, args=("login_comercio",))

# --- LOGIN PROPIETARIO ---
elif st.session_state.pagina == "login_comercio":
    st.subheader("🔑 Panel de Control")
    nom_login = st.text_input("Nombre de tu Negocio")
    if st.button("INGRESAR"):
        if nom_login:
            st.session_state.comercio_sesion = nom_login.strip()
            navegar("panel_carga")
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- PANEL DE GESTIÓN COMPLETO ---
elif st.session_state.pagina == "panel_carga":
    nombre_c = st.session_state.comercio_sesion
    st.markdown(f"<h2 style='color:#D4AF37;'>⚙️ Gestión: {nombre_c}</h2>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🚀 Cargar Nuevo", "📦 Inventario", "🖼️ Perfil & Contacto"])
    
    with t1:
        with st.form("carga_p", clear_on_submit=True):
            p_nom = st.text_input("Nombre del Producto")
            p_pre = st.number_input("Precio ($)", min_value=0.0)
            p_vid = st.file_uploader("Video (MP4)", type=['mp4'])
            if st.form_submit_button("🚀 PUBLICAR"):
                if p_nom and p_vid:
                    n_l = "".join(e for e in p_nom if e.isalnum())
                    path = f"productos/{n_l}_{random.randint(1000,9999)}.mp4"
                    supabase.storage.from_("fotos_productos").upload(path, p_vid.getvalue())
                    url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                    supabase.table("productos").insert({"nombre_producto": p_nom, "precio": p_pre, "video_url": url_v, "comercio_propietario": nombre_c}).execute()
                    st.success("✅ ¡Publicado con éxito!")
                    st.rerun()

    with t2:
        prods = supabase.table("productos").select("*").eq("comercio_propietario", nombre_c).execute()
        for p in prods.data:
            c1, c2 = st.columns([4, 1])
            c1.write(f"📦 **{p['nombre_producto']}** | {p['precio']}$")
            if c2.button("🗑️", key=f"del_{p['id']}"):
                supabase.table("productos").delete().eq("id", p['id']).execute()
                st.rerun()

    with t3:
        st.subheader("Configuración de Perfil de Venta")
        p_logo = st.file_uploader("Logo del Negocio", type=['jpg', 'png'])
        p_ws = st.text_input("WhatsApp (Ej: 584121234567)")
        p_info = st.text_area("Datos de Pago (Zelle, Pago Móvil, etc.)")
        if st.button("💾 GUARDAR CAMBIOS"):
            u_logo = None
            if p_logo:
                path_l = f"logos/{nombre_c}.jpg"
                supabase.storage.from_("fotos_productos").upload(path_l, p_logo.getvalue(), {"upsert": "true"})
                u_logo = supabase.storage.from_("fotos_productos").get_public_url(path_l)
            data = {"nombre_comercio": nombre_c, "whatsapp": p_ws, "datos_pago": p_info}
            if u_logo: data["logo_url"] = u_logo
            supabase.table("perfiles_comercio").upsert(data, on_conflict="nombre_comercio").execute()
            st.success("✅ Perfil actualizado")

    st.button("🔙 CERRAR SESIÓN", on_click=navegar, args=("inicio",))

# --- CENTRO COMERCIAL ---
elif st.session_state.pagina == "centro_comercial":
    st.markdown("<h1 class='title-luxury'>🛒 CENTRO COMERCIAL</h1>", unsafe_allow_html=True)
    res = supabase.table("perfiles_comercio").select("*").execute()
    for c in res.data:
        with st.container():
            st.markdown(f"<div class='card-luxury'><h3>💎 {c['nombre_comercio']}</h3></div>", unsafe_allow_html=True)
            st.button(f"ENTRAR A LA VITRINA", key=f"vis_{c['nombre_comercio']}", on_click=navegar, args=("vitrina_personal", c['nombre_comercio']))
    st.button("🔙 VOLVER AL INICIO", on_click=navegar, args=("inicio",))

# --- VITRINA CON CARRITO ---
elif st.session_state.pagina == "vitrina_personal":
    tienda = st.session_state.comercio_sel
    st.markdown(f"<h1 class='title-luxury'>{tienda}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
    total_acumulado = 0
    
    for p in prods.data:
        with st.container():
            st.video(p['video_url'])
            st.subheader(p['nombre_producto'])
            st.markdown(f"**Precio: {p['precio']}$**")
            
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

    if total_acumulado > 0:
        st.markdown(f"<div class='total-bar'>TOTAL DEL PEDIDO: {total_acumulado:.2f}$</div>", unsafe_allow_html=True)
        st.write("") # Espacio para la barra
        st.write("")
        st.button("🏁 FINALIZAR COMPRA", use_container_width=True, on_click=navegar, args=("pago",))
    
    st.button("🔙 VOLVER", on_click=navegar, args=("centro_comercial",))

# --- PÁGINA DE PAGO CON REFERENCIA ---
elif st.session_state.pagina == "pago":
    tienda = st.session_state.comercio_sel
    st.markdown(f"<h2 class='title-luxury'>🏁 PROCESAR PAGO</h2>", unsafe_allow_html=True)
    
    res_p = supabase.table("perfiles_comercio").select("*").eq("nombre_comercio", tienda).single().execute()
    perfil = res_p.data
    
    with st.container():
        st.markdown(f"<div class='card-luxury'><h4>💰 Datos de Pago para: {tienda}</h4><p>{perfil['datos_pago']}</p></div>", unsafe_allow_html=True)
        
        # CASILLA DE REFERENCIA (LO QUE PEDISTE)
        n_ref = st.text_input("🔢 Número de Referencia Bancaria", placeholder="Ej: 123456789")
        
        # Cálculo del pedido
        resumen = f"🛍️ *NUEVO PEDIDO - D'UNIG PLATINUM*%0A"
        resumen += f"━━━━━━━━━━━━━━━━━━%0A"
        prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
        total = 0
        for p in prods.data:
            cant = st.session_state.carrito.get(str(p['id']), 0)
            if cant > 0:
                resumen += f"✅ {p['nombre_producto']} (x{cant}): {p['precio']*cant}$%0A"
                total += p['precio']*cant
        
        resumen += f"━━━━━━━━━━━━━━━━━━%0A"
        resumen += f"💵 *TOTAL: {total:.2f}$*%0A"
        
        if n_ref:
            resumen += f"📌 *REF. BANCARIA:* {n_ref}%0A"
        
        st.write("---")
        if st.button("🚀 CONFIRMAR Y ENVIAR WHATSAPP", use_container_width=True):
            if not n_ref:
                st.warning("⚠️ Por favor, ingresa el número de referencia para continuar.")
            else:
                link = f"https://wa.me/{perfil['whatsapp']}?text={resumen}"
                st.markdown(f"""<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background:#25D366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold;">📲 CLICK AQUÍ PARA FINALIZAR EN WHATSAPP</div></a>""", unsafe_allow_html=True)

    st.button("🔙 REGRESAR A VITRINA", on_click=navegar, args=("vitrina_personal", tienda))
