import streamlit as st
from supabase import create_client, Client
import random
import re

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", initial_sidebar_state="collapsed")

try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("⚠️ Configura las credenciales de Supabase en Secrets.")
    st.stop()

def navegar(destino, com=None):
    st.session_state.pagina = destino
    if com: st.session_state.comercio_sel = com
    st.rerun()

# Estados de sesión
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None
if 'carrito' not in st.session_state: st.session_state.carrito = {}

# ==========================================
# 2. ESTILOS LUXURY ACTUALIZADOS
# ==========================================
st.markdown("""
    <style>
    .main { background: #0e1117; }
    .title-luxury { font-family: serif; color: #D4AF37; text-align: center; font-size: 2.8rem; }
    
    /* Botones Dorados */
    .stButton>button {
        background: linear-gradient(145deg, #d4af37, #b8860b);
        color: white !important; border-radius: 12px; font-weight: bold; width: 100%;
    }

    /* COLOR DIFERENTE PARA EL TOTAL (Azul Eléctrico Luxury) */
    .total-bar {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: #00d4ff; color: #000;
        text-align: center; padding: 15px; font-weight: 900; font-size: 22px;
        z-index: 1000; box-shadow: 0px -5px 15px rgba(0,212,255,0.4);
    }
    
    .card-tienda {
        background: rgba(255,255,255,0.03); border: 1px solid #D4AF37;
        padding: 20px; border-radius: 20px; text-align: center;
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
    with col1: st.button("🛒 EXPLORAR TIENDAS", on_click=navegar, args=("centro_comercial",))
    with col2: st.button("🏢 PANEL DE NEGOCIO", on_click=navegar, args=("registro_propietario",))

# --- REGISTRO / LOGIN PROPIETARIO ---
elif st.session_state.pagina == "registro_propietario":
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>🔐 ACCESO PRO</h2>", unsafe_allow_html=True)
    email = st.text_input("Ingresa tu Correo Electrónico")
    
    if st.button("SOLICITAR CÓDIGO DE ACCESO"):
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            # Aquí simulamos el envío. En el futuro puedes usar una API de email.
            st.session_state.codigo_gen = str(random.randint(1000, 9999))
            st.info(f"📧 Se ha enviado un código a {email} (Simulación: {st.session_state.codigo_gen})")
        else:
            st.error("Correo inválido.")
            
    codigo_ingresado = st.text_input("Introduce el código recibido", type="password")
    if st.button("VERIFICAR E INGRESAR"):
        if codigo_ingresado == st.session_state.get('codigo_gen'):
            st.session_state.user_email = email
            navegar("panel_carga")
        else:
            st.error("Código incorrecto.")
            
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- PANEL DE GESTIÓN (PERSISTENTE) ---
elif st.session_state.pagina == "panel_carga":
    email_u = st.session_state.user_email
    # Intentar recuperar perfil existente por email
    res_perfil = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_u).execute()
    perfil_data = res_perfil.data[0] if res_perfil.data else None
    
    st.title("⚙️ Mi Negocio")
    t1, t2, t3 = st.tabs(["🚀 Publicar", "📦 Stock", "🖼️ Mi Perfil"])
    
    with t3:
        st.subheader("Datos de Identidad")
        with st.form("perfil_form"):
            nombre_negocio = st.text_input("Nombre del Comercio", value=perfil_data['nombre_comercio'] if perfil_data else "")
            tel_ws = st.text_input("WhatsApp (Ej: 584121112233)", value=perfil_data['whatsapp'] if perfil_data else "")
            info_pago = st.text_area("Datos de Pago", value=perfil_data['datos_pago'] if perfil_data else "")
            logo_subir = st.file_uploader("Logo / Foto de Perfil", type=['jpg', 'png'])
            
            if st.form_submit_button("ACTUALIZAR PERFIL"):
                u_logo = perfil_data['logo_url'] if perfil_data else None
                if logo_subir:
                    path_l = f"logos/{email_u.replace('@','_')}.jpg"
# CORRECTO
supabase.storage.from_("fotos_productos").upload(
    path_l, 
    logo_subir.getvalue(), 
    {"upsert": True} # <--- Fíjate: True (sin comillas)
)
                up_data = {
                    "email_propietario": email_u,
                    "nombre_comercio": nombre_negocio,
                    "whatsapp": tel_ws,
                    "datos_pago": info_pago,
                    "logo_url": u_logo
                }
                supabase.table("perfiles_comercio").upsert(up_data, on_conflict="email_propietario").execute()
                st.success("✅ Perfil Guardado. Ahora es persistente.")
                st.rerun()

    with t1:
        if not perfil_data: st.warning("⚠️ Primero configura tu perfil en la pestaña 'Mi Perfil'.")
        else:
            with st.form("carga_p"):
                p_nom = st.text_input("Producto")
                p_pre = st.number_input("Precio ($)", min_value=0.0)
                p_vid = st.file_uploader("Video", type=['mp4'])
                if st.form_submit_button("SUBIR"):
                    path_v = f"prods/{random.randint(100,999)}.mp4"
                    supabase.storage.from_("fotos_productos").upload(path_v, p_vid.getvalue())
                    v_url = supabase.storage.from_("fotos_productos").get_public_url(path_v)
                    supabase.table("productos").insert({"nombre_producto": p_nom, "precio": p_pre, "video_url": v_url, "comercio_propietario": perfil_data['nombre_comercio']}).execute()
                    st.rerun()

    with t2:
        if perfil_data:
            prods = supabase.table("productos").select("*").eq("comercio_propietario", perfil_data['nombre_comercio']).execute()
            for p in prods.data:
                st.write(f"📦 {p['nombre_producto']} - {p['precio']}$")
                if st.button("Eliminar", key=f"d_{p['id']}"):
                    supabase.table("productos").delete().eq("id", p['id']).execute()
                    st.rerun()

    st.button("🔙 LOGOUT", on_click=navegar, args=("inicio",))

# --- VITRINA PERSONAL (NUEVO ORDEN DE BOTONES) ---
elif st.session_state.pagina == "vitrina_personal":
    tienda = st.session_state.comercio_sel
    st.markdown(f"<h1 class='title-luxury'>{tienda}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
    total = 0
    
    for p in prods.data:
        with st.container():
            st.video(p['video_url'])
            st.subheader(p['nombre_producto'])
            st.write(f"Precio: {p['precio']}$")
            
            id_p = str(p['id'])
            cant = st.session_state.carrito.get(id_p, 0)
            
            # FILA 1: Botones de cantidad
            c1, c2, c3 = st.columns([1,1,1])
            if c1.button("➖", key=f"min_{id_p}"):
                if cant > 0: st.session_state.carrito[id_p] = cant - 1; st.rerun()
            c2.markdown(f"<h3 style='text-align:center;'>{cant}</h3>", unsafe_allow_html=True)
            if c3.button("➕", key=f"add_{id_p}"):
                st.session_state.carrito[id_p] = cant + 1; st.rerun()
            
            # FILA 2: Botón de Pedido debajo (como pediste)
            if st.button("🛍️ AGREGAR ESTE PRODUCTO", key=f"btn_p_{id_p}"):
                st.toast("Añadido al carrito")
            
            total += cant * p['precio']
            st.write("---")

    if total > 0:
        st.markdown(f"<div class='total-bar'>TOTAL A PAGAR: {total:.2f}$</div>", unsafe_allow_html=True)
        st.write("<br><br>", unsafe_allow_html=True)
        st.button("🏁 FINALIZAR COMPRA", use_container_width=True, on_click=navegar, args=("pago",))
    
    st.button("🔙 VOLVER ATRÁS", on_click=navegar, args=("centro_comercial",))

# --- PAGO (Cierre del proceso) ---
elif st.session_state.pagina == "pago":
    tienda = st.session_state.comercio_sel
    st.markdown("<h2 class='title-luxury'>CONFIRMAR PAGO</h2>", unsafe_allow_html=True)
    ref = st.text_input("Referencia Bancaria")
    if st.button("ENVIAR POR WHATSAPP"):
        # Lógica de resumen y enlace wa.me ya conocida...
        st.success("Redirigiendo...")
    st.button("🔙 CANCELAR", on_click=navegar, args=("vitrina_personal", tienda))

# --- CENTRO COMERCIAL ---
elif st.session_state.pagina == "centro_comercial":
    st.markdown("<h1 class='title-luxury'>CENTRO COMERCIAL</h1>", unsafe_allow_html=True)
    res = supabase.table("perfiles_comercio").select("*").execute()
    for c in res.data:
        with st.container():
            st.markdown(f"<div class='card-tienda'><h3>💎 {c['nombre_comercio']}</h3></div>", unsafe_allow_html=True)
            st.button("VER VITRINA", key=f"v_{c['nombre_comercio']}", on_click=navegar, args=("vitrina_personal", c['nombre_comercio']))
    st.button("🔙 INICIO", on_click=navegar, args=("inicio",))
