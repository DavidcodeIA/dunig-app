import streamlit as st
from supabase import create_client, Client
import random

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN LUXURY
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", initial_sidebar_state="collapsed")

# Conexión Segura a Supabase
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("⚠️ Error de conexión: Revisa tus Secrets en Streamlit Cloud.")
    st.stop()

# --- FUNCIÓN DE NAVEGACIÓN ---
def navegar(destino, com=None):
    st.session_state.pagina = destino
    if com:
        st.session_state.comercio_sel = com
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
    
    .title-luxury {
        font-family: 'Playfair Display', serif;
        color: #D4AF37;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        font-size: 3rem;
    }

    /* Botones 3D Estilo Platinum */
    .stButton>button {
        background: linear-gradient(145deg, #d4af37, #b8860b);
        color: white !important;
        border: none;
        padding: 15px 25px;
        border-radius: 12px;
        box-shadow: 0px 6px 0px #8b6d05, 0px 10px 15px rgba(0,0,0,0.4);
        transition: all 0.2s ease;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(2px);
        box-shadow: 0px 4px 0px #8b6d05, 0px 6px 10px rgba(0,0,0,0.3);
    }
    
    .stButton>button:active {
        transform: translateY(6px);
        box-shadow: none;
    }

    .card-luxury {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(212, 175, 55, 0.3);
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
        text-align: center;
    }
    
    .price-tag { color: #D4AF37; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE PÁGINAS
# ==========================================

# --- PÁGINA: INICIO ---
if st.session_state.pagina == "inicio":
    st.markdown("<h1 class='title-luxury'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("🛒 ENTRAR AL CENTRO COMERCIAL", on_click=navegar, args=("centro_comercial",), key="btn_cliente")
    with col2:
        st.button("🏢 ACCESO PROPIETARIOS", on_click=navegar, args=("login_comercio",), key="btn_admin")

# --- PÁGINA: LOGIN PROPIETARIO ---
elif st.session_state.pagina == "login_comercio":
    st.markdown("<h2 style='color:#D4AF37; text-align:center;'>🔑 ACCESO PRIVADO</h2>", unsafe_allow_html=True)
    nom_login = st.text_input("Nombre de tu Negocio", placeholder="Ej: Pizzería Dante")
    
    if st.button("INGRESAR AL PANEL"):
        if nom_login:
            st.session_state.comercio_sesion = nom_login.strip()
            navegar("panel_carga")
        else:
            st.warning("Escribe el nombre de tu negocio.")
    
    st.button("🔙 VOLVER AL INICIO", on_click=navegar, args=("inicio",), key="back_login")

# --- PÁGINA: PANEL DE GESTIÓN (CARGA) ---
elif st.session_state.pagina == "panel_carga":
    nombre_c = st.session_state.comercio_sesion
    st.title(f"⚙️ Gestión: {nombre_c}")
    
    # SECCIÓN PERFIL INSTANTÁNEO
    with st.expander("🖼️ CONFIGURAR PERFIL (Logo, WhatsApp, Pago)", expanded=True):
        logo = st.file_uploader("Tomar foto o subir Logo", type=['jpg', 'png', 'jpeg'])
        ws = st.text_input("WhatsApp (Ej: 584121234567)")
        pago = st.text_area("Datos para el Pago (Zelle, Pago Móvil, etc.)")
        
        if st.button("✨ GUARDAR Y ACTUALIZAR PERFIL"):
            try:
                url_l = None
                if logo:
                    path = f"logos/{nombre_c}_{random.randint(100,999)}.jpg"
                    supabase.storage.from_("fotos_productos").upload(path, logo.getvalue())
                    url_l = supabase.storage.from_("fotos_productos").get_public_url(path)
                
                data_perfil = {"nombre_comercio": nombre_c, "whatsapp": ws, "datos_pago": pago}
                if url_l: data_perfil["logo_url"] = url_l
                
                supabase.table("perfiles_comercio").upsert(data_perfil, on_conflict="nombre_comercio").execute()
                st.success("✅ Perfil actualizado al instante.")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # SECCIÓN CARGA PRODUCTO INSTANTÁNEA
    with st.form("form_carga_video", clear_on_submit=True):
        st.subheader("🎬 Publicar Video-Producto")
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        p_vid = st.file_uploader("Grabar o subir Video (MP4)", type=['mp4'])
        
        if st.form_submit_button("🚀 PUBLICAR EN VITRINA"):
            if p_nom and p_vid:
                with st.spinner("Subiendo a la nube..."):
                    try:
                        nombre_limpio = "".join(e for e in p_nom if e.isalnum())
                        path_v = f"productos/{nombre_limpio}_{random.randint(1000,9999)}.mp4"
                        supabase.storage.from_("fotos_productos").upload(path_v, p_vid.getvalue())
                        url_v = supabase.storage.from_("fotos_productos").get_public_url(path_v)
                        
                        supabase.table("productos").insert({
                            "nombre_producto": p_nom, "precio": p_pre, 
                            "video_url": url_v, "comercio_propietario": nombre_c
                        }).execute()
                        st.balloons()
                        st.success("✅ ¡Video publicado!")
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Faltan datos o el video.")

    st.button("🔙 SALIR", on_click=navegar, args=("inicio",))

# --- PÁGINA: CENTRO COMERCIAL ---
elif st.session_state.pagina == "centro_comercial":
    st.markdown("<h1 class='title-luxury'>🛒 CENTRO COMERCIAL</h1>", unsafe_allow_html=True)
    try:
        comercios = supabase.table("perfiles_comercio").select("*").execute()
        if comercios.data:
            for c in comercios.data:
                with st.container():
                    st.markdown(f"<div class='card-luxury'><h3>💎 {c['nombre_comercio']}</h3></div>", unsafe_allow_html=True)
                    st.button(f"VISITAR TIENDA", key=f"v_{c['nombre_comercio']}", 
                              on_click=navegar, args=("vitrina_personal", c['nombre_comercio']))
                    st.write("")
        else:
            st.info("Aún no hay comercios registrados.")
    except Exception as e:
        st.error(f"Error: {e}")
    
    st.button("🔙 VOLVER AL INICIO", on_click=navegar, args=("inicio",))

# --- PÁGINA: VITRINA PERSONAL ---
elif st.session_state.pagina == "vitrina_personal":
    tienda_nom = st.session_state.comercio_sel
    st.markdown(f"<h1 class='title-luxury'>{tienda_nom}</h1>", unsafe_allow_html=True)
    
    try:
        prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda_nom).execute()
        if prods.data:
            for p in prods.data:
                with st.container():
                    st.video(p['video_url'])
                    st.subheader(f"✨ {p['nombre_producto']}")
                    st.markdown(f"<p class='price-tag'>{p['precio']}$</p>", unsafe_allow_html=True)
                    if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}"):
                        st.session_state.carrito[str(p['id'])] = 1
                        navegar("pago")
                    st.write("---")
        else:
            st.warning("Esta tienda aún no tiene productos.")
    except Exception as e:
        st.error(f"Error: {e}")
        
    st.button("🔙 VOLVER AL CENTRO", on_click=navegar, args=("centro_comercial",))

# --- PÁGINA: PROCESAR PAGO ---
elif st.session_state.pagina == "pago":
    st.markdown("<h1 class='title-luxury'>🏁 FINALIZAR COMPRA</h1>", unsafe_allow_html=True)
    # Lógica de cierre y WhatsApp...
    st.button("🔙 REGRESAR A VITRINA", on_click=navegar, args=("vitrina_personal", st.session_state.comercio_sel))
