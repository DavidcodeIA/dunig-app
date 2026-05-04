import streamlit as st
from supabase import create_client, Client
import random
import re

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", initial_sidebar_state="collapsed")

# Conexión Segura
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("⚠️ Configura las credenciales de Supabase en Secrets.")
    st.stop()

# Función de Navegación con Efecto Rerun
def navegar(destino, com=None):
    st.session_state.pagina = destino
    if com: st.session_state.comercio_sel = com
    st.rerun()

# Estados de sesión iniciales
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None
if 'carrito' not in st.session_state: st.session_state.carrito = {}

# ==========================================
# 2. ESTILOS LUXURY & ANIMACIONES (ULTRA GENERACIÓN)
# ==========================================
st.markdown("""
    <style>
    /* Animación de entrada de página */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main { 
        background: radial-gradient(circle at top, #1a1a1a, #000000); 
        animation: fadeInUp 0.8s ease-out;
    }

    .title-luxury { 
        font-family: 'Playfair Display', serif; 
        color: #D4AF37; 
        text-align: center; 
        font-size: 3.5rem;
        text-shadow: 0px 0px 20px rgba(212, 175, 55, 0.5);
        letter-spacing: 2px;
    }

    /* Botones Dorados con Brillo Dinámico */
    .stButton>button {
        background: linear-gradient(135deg, #D4AF37 0%, #8B6B1E 100%);
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 12px 25px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        text-transform: uppercase;
    }

    .stButton>button:hover {
        transform: scale(1.03) translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.4) !important;
        background: linear-gradient(135deg, #f1c40f 0%, #D4AF37 100%) !important;
    }

    /* Barra de Total Luxury Neon */
    .total-bar {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: rgba(0, 212, 255, 0.9); 
        backdrop-filter: blur(10px);
        color: #000;
        text-align: center; padding: 18px; 
        font-weight: 900; font-size: 24px;
        z-index: 1000; box-shadow: 0px -10px 30px rgba(0,212,255,0.3);
        border-top: 2px solid #fff;
    }
    
    /* Card de Tienda Glassmorphism */
    .card-tienda {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(212, 175, 55, 0.3);
        padding: 25px;
        border-radius: 25px;
        text-align: center;
        backdrop-filter: blur(5px);
        transition: 0.4s;
    }
    .card-tienda:hover {
        border: 1px solid #D4AF37;
        background: rgba(212, 175, 55, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE NAVEGACIÓN
# ==========================================

# --- INICIO ---
if st.session_state.pagina == "inicio":
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='title-luxury'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>ELITE SHOPPING EXPERIENCE</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1: st.button("🛒 EXPLORAR TIENDAS", on_click=navegar, args=("centro_comercial",))
    with col2: st.button("🏢 PANEL DE NEGOCIO", on_click=navegar, args=("registro_propietario",))

# --- REGISTRO / LOGIN PROPIETARIO ---
elif st.session_state.pagina == "registro_propietario":
    st.markdown("<h2 class='title-luxury'>🔐 ACCESO EXCLUSIVO</h2>", unsafe_allow_html=True)
    with st.container():
        email = st.text_input("Correo Electrónico")
        
        if st.button("SOLICITAR CÓDIGO"):
            if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.session_state.codigo_gen = str(random.randint(1000, 9999))
                st.info(f"📧 Código enviado (Simulación: {st.session_state.codigo_gen})")
            else:
                st.error("Formato de correo inválido.")
                
        codigo_ingresado = st.text_input("Código de Seguridad", type="password")
        if st.button("ENTRAR AL SISTEMA"):
            if codigo_ingresado == st.session_state.get('codigo_gen'):
                st.session_state.user_email = email
                navegar("panel_carga")
            else:
                st.error("Código incorrecto.")
                
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- PANEL DE GESTIÓN ---
elif st.session_state.pagina == "panel_carga":
    email_u = st.session_state.user_email
    res_perfil = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_u).execute()
    perfil_data = res_perfil.data[0] if res_perfil.data else None
    
    st.markdown(f"<h2 class='title-luxury'>⚙️ GESTIÓN: {perfil_data['nombre_comercio'] if perfil_data else 'Nuevo Negocio'}</h2>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🚀 PUBLICAR", "📦 MI STOCK", "🖼️ CONFIGURAR PERFIL"])
    
    with t3:
        with st.form("perfil_form"):
            nombre_negocio = st.text_input("Nombre de la Marca", value=perfil_data['nombre_comercio'] if perfil_data else "")
            tel_ws = st.text_input("WhatsApp (Ej: 584121112233)", value=perfil_data['whatsapp'] if perfil_data else "")
            info_pago = st.text_area("Métodos de Pago", value=perfil_data['datos_pago'] if perfil_data else "")
            logo_subir = st.file_uploader("Subir Logo (PNG/JPG)", type=['jpg', 'png'])
            
            if st.form_submit_button("GUARDAR CAMBIOS"):
                u_logo = perfil_data['logo_url'] if perfil_data else None
                if logo_subir:
                    path_l = f"logos/{email_u.replace('@','_')}.jpg"
                    # CORRECCIÓN DE LA SUBIDA
                    supabase.storage.from_("fotos_productos").upload(path_l, logo_subir.getvalue(), {"upsert": "True"})
                    u_logo = supabase.storage.from_("fotos_productos").get_public_url(path_l)

                up_data = {
                    "email_propietario": email_u,
                    "nombre_comercio": nombre_negocio,
                    "whatsapp": tel_ws,
                    "datos_pago": info_pago,
                    "logo_url": u_logo
                }
                supabase.table("perfiles_comercio").upsert(up_data, on_conflict="email_propietario").execute()
                st.success("✅ Perfil actualizado.")
                st.rerun()

    with t1:
        if not perfil_data: st.warning("⚠️ Configura tu perfil primero.")
        else:
            with st.form("carga_p"):
                p_nom = st.text_input("Nombre del Producto")
                p_pre = st.number_input("Precio ($)", min_value=0.0)
                p_vid = st.file_uploader("Video del Producto", type=['mp4'])
                if st.form_submit_button("Lanzar Producto"):
                    if p_nom and p_vid:
                        path_v = f"prods/{random.randint(10000,99999)}.mp4"
                        supabase.storage.from_("fotos_productos").upload(path_v, p_vid.getvalue())
                        v_url = supabase.storage.from_("fotos_productos").get_public_url(path_v)
                        supabase.table("productos").insert({
                            "nombre_producto": p_nom, 
                            "precio": p_pre, 
                            "video_url": v_url, 
                            "comercio_propietario": perfil_data['nombre_comercio']
                        }).execute()
                        st.success("Producto en vitrina!")
                        st.rerun()

    with t2:
        if perfil_data:
            prods = supabase.table("productos").select("*").eq("comercio_propietario", perfil_data['nombre_comercio']).execute()
            for p in prods.data:
                col_p, col_b = st.columns([4,1])
                col_p.write(f"🏷️ **{p['nombre_producto']}** - ${p['precio']}")
                if col_b.button("🗑️", key=f"del_{p['id']}"):
                    supabase.table("productos").delete().eq("id", p['id']).execute()
                    st.rerun()

    st.button("🔙 CERRAR SESIÓN", on_click=navegar, args=("inicio",))

# --- VITRINA PERSONAL ---
elif st.session_state.pagina == "vitrina_personal":
    tienda = st.session_state.comercio_sel
    st.markdown(f"<h1 class='title-luxury'>{tienda}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
    total = 0
    
    for p in prods.data:
        with st.container():
            st.video(p['video_url'])
            st.subheader(p['nombre_producto'])
            st.markdown(f"<h4 style='color:#D4AF37;'>Precio: {p['precio']}$</h4>", unsafe_allow_html=True)
            
            id_p = str(p['id'])
            cant = st.session_state.carrito.get(id_p, 0)
            
            c1, c2, c3 = st.columns([1,1,1])
            if c1.button("➖", key=f"m_{id_p}"):
                if cant > 0: 
                    st.session_state.carrito[id_p] = cant - 1
                    st.rerun()
            c2.markdown(f"<h3 style='text-align:center;'>{cant}</h3>", unsafe_allow_html=True)
            if c3.button("➕", key=f"a_{id_p}"):
                st.session_state.carrito[id_p] = cant + 1
                st.rerun()
            
            if st.button("🛍️ CONFIRMAR CANTIDAD", key=f"btn_{id_p}"):
                st.toast(f"{p['nombre_producto']} actualizado")
            
            total += cant * p['precio']
            st.write("---")

    if total > 0:
        st.markdown(f"<div class='total-bar'>TOTAL A PAGAR: {total:.2f}$</div>", unsafe_allow_html=True)
        st.write("<br><br><br>", unsafe_allow_html=True)
        st.button("🏁 FINALIZAR COMPRA", use_container_width=True, on_click=navegar, args=("pago",))
    
    st.button("🔙 VOLVER AL CENTRO", on_click=navegar, args=("centro_comercial",))

# --- CENTRO COMERCIAL ---
elif st.session_state.pagina == "centro_comercial":
    st.markdown("<h1 class='title-luxury'>CENTRO COMERCIAL PLATINUM</h1>", unsafe_allow_html=True)
    res = supabase.table("perfiles_comercio").select("*").execute()
    
    cols = st.columns(2)
    for idx, c in enumerate(res.data):
        with cols[idx % 2]:
            st.markdown(f"""
                <div class='card-tienda'>
                    <img src='{c['logo_url']}' style='width:100px; border-radius:50%; border:2px solid #D4AF37;'>
                    <h3>{c['nombre_comercio']}</h3>
                </div>
            """, unsafe_allow_html=True)
            st.button(f"ENTRAR A {c['nombre_comercio']}", key=f"sh_{idx}", on_click=navegar, args=("vitrina_personal", c['nombre_comercio']))
            st.markdown("<br>", unsafe_allow_html=True)

    st.button("🔙 INICIO", on_click=navegar, args=("inicio",))
