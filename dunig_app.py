import streamlit as st
from supabase import create_client, Client
import urllib.parse
import uuid

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_data' not in st.session_state: st.session_state.user_data = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000000; color: #ffffff; }
    
    /* BOTÓN COMPRAR */
    .btn-comprar button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 55px !important; width: 100% !important;
    }

    /* BOTÓN REGRESAR MINIMALISTA */
    .btn-regresar button {
        background: transparent !important; color: rgba(255,255,255,0.6) !important; 
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important; height: 30px !important;
        width: 100% !important; font-size: 0.7rem !important;
        text-transform: uppercase; letter-spacing: 2px;
    }

    /* VIDEO Y CONTENEDORES */
    .video-full { width: 100vw; position: relative; left: 50%; right: 50%; margin-left: -50vw; margin-right: -50vw; }
    video { width: 100% !important; height: auto !important; max-height: 80vh; object-fit: cover; }

    .info-luxury-box {
        display: flex; justify-content: space-between; align-items: center;
        background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);
        padding: 0 15px; height: 50px; border-radius: 12px; border: 1px solid rgba(212,175,55,0.4);
    }
    .p-title { color: #D4AF37; font-weight: 700; text-transform: uppercase; font-size: 0.9rem; }
    .p-price { color: #39FF14; font-weight: 900; font-size: 1.1rem; }

    .img-cuadrada { width: 100%; aspect-ratio: 1/1; object-fit: cover; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================

es_admin = st.query_params.get("admin") == "true"

if es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL PROFESIONAL</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        m = st.text_input("Email de Socio")
        c = st.text_input("PIN Secreto", type="password")
        if st.button("ABRIR PANEL"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m.lower()).execute()
            if res.data and str(res.data[0]['codigo_acceso']).upper() == c.upper():
                st.session_state.logged_in = True
                st.session_state.user_data = res.data[0]
                st.rerun()
    else:
        u = st.session_state.user_data
        tab1, tab2, tab3 = st.tabs(["📦 INVENTARIO", "🖼️ MI MARCA", "💰 PAGOS"])

        # --- TAB 1: PRODUCTOS (SUBIR Y BORRAR) ---
        with tab1:
            with st.expander("➕ PUBLICAR NUEVO VIDEO"):
                with st.form("nuevo_p", clear_on_submit=True):
                    nom = st.text_input("Nombre del Producto")
                    pre = st.number_input("Precio ($)", min_value=0.0)
                    vid = st.file_uploader("Video (MP4)", type=['mp4'])
                    if st.form_submit_button("SUBIR A LA TIENDA"):
                        if nom and vid:
                            v_path = f"videos/{u['nombre_comercio']}/{uuid.uuid4()}.mp4"
                            supabase.storage.from_("fotos_productos").upload(v_path, vid.getvalue())
                            v_url = supabase.storage.from_("fotos_productos").get_public_url(v_path)
                            supabase.table("productos").insert({"nombre_producto": nom, "precio": pre, "video_url": v_url, "comercio_relacionado": u['nombre_comercio']}).execute()
                            st.success("¡Publicado con éxito!")
                            st.rerun()

            st.subheader("Tus Videos en Vivo")
            mis_prods = supabase.table("productos").select("*").eq("comercio_relacionado", u['nombre_comercio']).execute().data
            for mp in mis_prods:
                c1, c2 = st.columns([5, 1])
                c1.info(f"🎥 {mp['nombre_producto']} - ${mp['precio']}")
                if c2.button("🗑️", key=f"del_{mp['id']}"):
                    supabase.table("productos").delete().eq("id", mp['id']).execute()
                    st.rerun()

        # --- TAB 2: PERFIL (CAMBIAR PORTADA) ---
        with tab2:
            st.subheader("Portada del Mall")
            st.image(u['portada_url'], width=150)
            nueva_img = st.file_uploader("Actualizar foto de portada", type=['jpg', 'png'])
            if st.button("GUARDAR NUEVA PORTADA"):
                if nueva_img:
                    p_path = f"portadas/{uuid.uuid4()}.jpg"
                    supabase.storage.from_("fotos_productos").upload(p_path, nueva_img.getvalue())
                    p_url = supabase.storage.from_("fotos_productos").get_public_url(p_path)
                    supabase.table("perfiles_comercio").update({"portada_url": p_url}).eq("id", u['id']).execute()
                    st.success("Imagen de marca actualizada")
                    st.rerun()

        # --- TAB 3: DATOS DE PAGO ---
        with tab3:
            st.subheader("Métodos de Recepción")
            pago_previo = u.get('datos_pago', "")
            txt_pago = st.text_area("Escribe tus datos (Zelle, Pago Móvil, etc.)", value=pago_previo)
            if st.button("ACTUALIZAR DATOS DE PAGO"):
                supabase.table("perfiles_comercio").update({"datos_pago": txt_pago}).eq("id", u['id']).execute()
                st.success("Datos guardados")
                st.rerun()
        
        if st.button("SALIR DEL PANEL"):
            st.session_state.logged_in = False
            st.rerun()

# --- VISTA: MALL ---
elif st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    cols = st.columns(2)
    for i, t in enumerate(tiendas):
        with cols[i % 2]:
            st.markdown(f'<img src="{t["portada_url"]}" class="img-cuadrada">', unsafe_allow_html=True)
            if st.button(f"ENTRAR {t['nombre_comercio'].upper()}", key=f"t_{t['id']}"):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA: TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        st.markdown('<div class="video-full">', unsafe_allow_html=True)
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-luxury-box"><span class="p-title">{p["nombre_producto"]}</span><span class="p-price">${p["precio"]}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="btn-comprar">', unsafe_allow_html=True)
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            pago = t.get('datos_pago', 'Consultar al privado')
            msj = urllib.parse.quote(f"¡Hola! Quiero comprar {p['nombre_producto']}. Ya vi tus métodos de pago: {pago}")
            st.link_button("CONFIRMAR POR WHATSAPP", f"https://wa.me/{t['whatsapp']}?text={msj}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="btn-regresar">', unsafe_allow_html=True)
        if st.button("REGRESAR AL MALL", key=f"back_{p['id']}"):
            ir_a('mall')
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()