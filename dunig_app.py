import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

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

# Configuración de Planes y Beneficios
PLANES_INFO = {
    "GRATUITO": {"precio": "0", "limite": 3, "beneficios": "3 productos, Soporte básico."},
    "BRONCE": {"precio": "5", "limite": 10, "beneficios": "10 productos, Etiqueta Bronce."},
    "PLATA": {"precio": "15", "limite": 25, "beneficios": "25 productos, Destacados."},
    "ORO": {"precio": "30", "limite": 999, "beneficios": "Ilimitados, Gestión VIP."}
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS ULTRA-INMERSIVO (BOTONES PEGADOS)
# ==========================================
st.markdown("""
    <style>
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #000; }
    header { visibility: hidden; }
    
    .video-wrapper {
        position: relative;
        width: 100%;
        aspect-ratio: 9 / 16;
        background: #000;
        margin-bottom: 0px !important;
    }

    .stVideo { width: 100% !important; margin: 0 !important; }
    .stVideo video { object-fit: cover !important; border-radius: 0px !important; }

    /* Overlay: Precio y Nombre */
    .overlay-info {
        position: absolute;
        bottom: 40px;
        left: 15px;
        z-index: 100;
    }

    .burbuja-precio-in {
        background: linear-gradient(135deg, #D4AF37, #F9F295);
        color: #000;
        padding: 4px 12px;
        border-radius: 4px;
        font-weight: 900;
        font-size: 1.2rem;
        display: inline-block;
    }

    .nombre-in {
        color: #fff;
        font-size: 1.6rem;
        font-weight: 800;
        text-shadow: 2px 2px 8px #000;
        margin-top: 8px;
        text-transform: uppercase;
    }

    /* Botones de Acción Pegados */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #8A6E2F) !important;
        color: #000 !important;
        border-radius: 0px !important;
        font-weight: 800 !important;
        border: none !important;
        height: 60px;
        width: 100% !important;
        margin: 0 !important;
    }
    
    div.stVerticalBlock { gap: 0rem !important; }
    div[data-testid="stVerticalBlock"] > div { padding: 0 !important; margin: 0 !important; }
    
    .img-mall { width: 100%; aspect-ratio: 1/1; object-fit: cover; border: 1px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_reg = st.query_params.get("reg") == "true"

# --- VISTA REGISTRO ---
if es_reg:
    st.markdown("<h2 style='text-align:center; color:#D4AF37; padding:20px;'>REGISTRO SOCIO LUXURY</h2>", unsafe_allow_html=True)
    
    c_plans = st.columns(4)
    for i, (p_name, p_val) in enumerate(PLANES_INFO.items()):
        with c_plans[i]:
            st.info(f"**{p_name}**\n\n${p_val['precio']}\n\n{p_val['beneficios']}")

    with st.form("reg_form"):
        n_m = st.text_input("Nombre de Marca")
        e_m = st.text_input("Email Propietario")
        w_m = st.text_input("WhatsApp (Ej: 58412...)")
        p_m = st.selectbox("Elegir Plan", list(PLANES_INFO.keys()))
        l_m = st.file_uploader("Logo / Portada", type=['jpg', 'png'])
        if st.form_submit_button("UNIRSE A D'UNIG"):
            if n_m and l_m:
                path = f"logos/{random.randint(100,999)}_{n_m}.jpg"
                supabase.storage.from_("fotos_productos").upload(path, l_m.getvalue())
                url_f = supabase.storage.from_("fotos_productos").get_public_url(path)
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": n_m, "email_propietario": e_m.lower(),
                    "whatsapp": w_m, "portada_url": url_f, "plan": p_m, "codigo_acceso": "LUXURY1"
                }).execute()
                st.success("¡Registro Exitoso! Entra como Admin.")

# --- VISTA USUARIO ---
elif not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h2 style='text-align:center; color:#D4AF37; padding:15px;'>D'UNIG MALL</h2>", unsafe_allow_html=True)
        tiendas = supabase.table("perfiles_comercio").select("*").execute().data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.markdown(f'<img src="{t["portada_url"]}" class="img-mall">', unsafe_allow_html=True)
                        if st.button(t['nombre_comercio'].upper(), key=f"t_{t['id']}"):
                            st.session_state.tienda_actual = t; ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        
        for p in prods:
            st.markdown(f"""
                <div class="video-wrapper">
                    <div class="overlay-info">
                        <div class="burbuja-precio-in">${p['precio']}</div>
                        <div class="nombre-in">{p['nombre_producto']}</div>
                    </div>
            """, unsafe_allow_html=True)
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("⬅️ MALL", key=f"back_{p['id']}"): ir_a('mall')
            with c2:
                msj = f"Hola {t['nombre_comercio']}, me interesa {p['nombre_producto']} (${p['precio']})"
                st.link_button("🛒 COMPRAR", f"https://wa.me/{t['whatsapp']}?text={urllib.parse.quote(msj)}")

# --- VISTA PANEL DE CONTROL (ADMIN) ---
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL D'UNIG</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.container(border=True):
            user_log = st.text_input("Email").lower()
            pass_log = st.text_input("Código de Acceso", type="password")
            if st.button("ENTRAR AL PANEL"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", user_log).execute()
                if res.data and str(res.data[0]['codigo_acceso']) == pass_log:
                    st.session_state.logged_in = True
                    st.session_state.user_email = user_log
                    st.rerun()
                else: st.error("Acceso incorrecto")
    else:
        # Recuperar datos del socio
        p_data = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        
        tab1, tab2, tab3 = st.tabs(["💎 PRODUCTOS", "🖼️ PERFIL", "💳 PLAN"])
        
        with tab1:
            mis_p = supabase.table("productos").select("*").eq("comercio_relacionado", p_data['nombre_comercio']).execute().data
            limit = PLANES_INFO.get(p_data['plan'], {"limite": 3})['limite']
            st.write(f"Productos: **{len(mis_p)} / {limit}**")
            
            if len(mis_p) < limit:
                with st.expander("➕ SUBIR NUEVO VIDEO"):
                    with st.form("subir_p"):
                        n = st.text_input("Nombre")
                        pr = st.number_input("Precio ($)", min_value=0.0)
                        vi = st.file_uploader("Video Vertical (MP4)", type=['mp4'])
                        if st.form_submit_button("PUBLICAR"):
                            v_path = f"v/{random.randint(100,999)}_{p_data['id']}.mp4"
                            supabase.storage.from_("fotos_productos").upload(v_path, vi.getvalue())
                            v_url = supabase.storage.from_("fotos_productos").get_public_url(v_path)
                            supabase.table("productos").insert({
                                "nombre_producto": n, "precio": pr, "video_url": v_url,
                                "comercio_relacionado": p_data['nombre_comercio']
                            }).execute()
                            st.success("Publicado"); st.rerun()
            
            st.divider()
            for mp in mis_p:
                col_i, col_d = st.columns([4, 1])
                col_i.write(f"📦 {mp['nombre_producto']} - ${mp['precio']}")
                if col_d.button("🗑️", key=f"del_{mp['id']}"):
                    supabase.table("productos").delete().eq("id", mp['id']).execute()
                    st.success("Eliminado"); st.rerun()

        with tab2:
            st.image(p_data['portada_url'], width=100)
            st.write(f"Tienda: **{p_data['nombre_comercio']}**")
            new_pay = st.text_area("Datos de Pago (Se verán al vender)", value=p_data.get('datos_pago', ''))
            if st.button("GUARDAR CAMBIOS"):
                supabase.table("perfiles_comercio").update({"datos_pago": new_pay}).eq("id", p_data['id']).execute()
                st.success("Guardado")

        with tab3:
            st.write(f"Tu plan actual: **{p_data['plan']}**")
            st.info("Para subir de nivel, contacta a D'UNIG Central.")
            if st.button("🚪 CERRAR SESIÓN"):
                st.session_state.logged_in = False
                st.rerun()