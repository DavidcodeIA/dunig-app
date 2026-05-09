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
# 2. ESTÉTICA INMERSIVA (ICONOS DENTRO)
# ==========================================
st.markdown("""
    <style>
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #000; }
    header { visibility: hidden; }
    
    /* El video ocupa todo el contenedor */
    .video-canvas {
        position: relative;
        width: 100%;
        aspect-ratio: 9 / 16;
        background: #000;
        overflow: hidden;
        margin-bottom: 2px; /* Espacio mínimo entre videos */
    }

    .stVideo { width: 100% !important; margin: 0 !important; }
    .stVideo video { object-fit: cover !important; border-radius: 0px !important; height: 100% !important; }

    /* --- ICONOS FLOTANTES (DENTRO DEL VIDEO) --- */
    
    /* 1. Flecha Regresar (Izquierda Media) */
    .btn-volver-float {
        position: absolute; top: 50%; left: 15px; transform: translateY(-50%);
        z-index: 101;
    }

    /* 2. Burbuja de Dinero/Precio (Izquierda abajo de la flecha) */
    .btn-precio-float {
        position: absolute; top: 62%; left: 15px;
        z-index: 101;
    }

    /* 3. Punto de Venta / Pagar (Izquierda abajo del precio) */
    .btn-pagar-float {
        position: absolute; top: 75%; left: 15px;
        z-index: 101;
    }

    /* 4. Textos (Abajo a la izquierda) */
    .textos-float {
        position: absolute; bottom: 30px; left: 15px;
        z-index: 101;
        text-align: left;
        pointer-events: none;
    }

    /* Estilo de los Botones de Iconos */
    .stButton>button.icon-only {
        background: none !important; border: none !important;
        font-size: 45px !important; /* Tamaño grande como en tu ejemplo */
        color: #fff !important; padding: 0 !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
    }

    .price-tag-luxury {
        background: linear-gradient(135deg, #D4AF37, #F9F295);
        color: #000; padding: 5px 15px; border-radius: 50px;
        font-weight: 900; font-size: 1.4rem;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.6);
    }

    .label-comercio { font-size: 1.5rem; font-weight: 900; color: #1E4D92; text-shadow: 1px 1px 2px #fff; }
    .label-producto { font-size: 1.8rem; font-weight: 900; color: #1E4D92; text-shadow: 1px 1px 2px #fff; }

    .img-mall { width: 100%; aspect-ratio: 1/1; object-fit: cover; border: 1px solid #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DE PAGO
# ==========================================
@st.dialog("💎 PUNTO DE VENTA")
def ventana_pago(p, t):
    st.markdown(f"### ✨ {p['nombre_producto']}")
    st.write(f"Vendedor: **{t['nombre_comercio']}**")
    ref = st.text_input("Referencia de Pago")
    if st.button("CONFIRMAR PAGO"):
        msj = f"PAGO REALIZADO: {p['nombre_producto']} - Ref: {ref}"
        st.link_button("INFORMAR AL VENDEDOR", f"https://wa.me/{t['whatsapp']}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_reg = st.query_params.get("reg") == "true"

if es_reg:
    st.title("REGISTRO D'UNIG")
    # ... (Se mantiene lógica de registro anterior)

elif not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h2 style='text-align:center; color:#D4AF37; padding:20px;'>🏙️ D'UNIG MALL</h2>", unsafe_allow_html=True)
        tiendas = supabase.table("perfiles_comercio").select("*").execute().data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.markdown(f'<img src="{t["portada_url"]}" class="img-mall">', unsafe_allow_html=True)
                        if st.button(t['nombre_comercio'].upper(), key=f"t_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t; ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        
        for p in prods:
            # TODO EL CONTENIDO DENTRO DEL VIDEO
            st.markdown(f'<div class="video-canvas">', unsafe_allow_html=True)
            
            # 1. Flecha Volver
            st.markdown('<div class="btn-volver-float">', unsafe_allow_html=True)
            if st.button("↩️", key=f"v_{p['id']}", help="icon-only"): ir_a('mall')
            st.markdown('</div>', unsafe_allow_html=True)

            # 2. Burbuja Precio (Simbolizando el dinero)
            st.markdown(f'<div class="btn-precio-float"><div class="price-tag-luxury">{p["precio"]}$</div></div>', unsafe_allow_html=True)

            # 3. Punto de Venta (Icono Pagar)
            st.markdown('<div class="btn-pagar-float">', unsafe_allow_html=True)
            if st.button("💳", key=f"p_{p['id']}", help="icon-only"): ventana_pago(p, t)
            st.markdown('</div>', unsafe_allow_html=True)

            # 4. Textos de Identificación
            st.markdown(f"""
                <div class="textos-float">
                    <div class="label-comercio">{t['nombre_comercio']}</div>
                    <div class="label-producto">{p['nombre_producto']}</div>
                </div>
            """, unsafe_allow_html=True)

            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # --- PANEL ADMIN (ESTRUCTURA COMPLETA) ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL ADMIN</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        u = st.text_input("Email")
        c = st.text_input("Código", type="password")
        if st.button("ENTRAR"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", u.lower()).execute()
            if res.data and str(res.data[0]['codigo_acceso']) == c:
                st.session_state.logged_in = True; st.session_state.user_email = u; st.rerun()
    else:
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        t1, t2 = st.tabs(["MIS PRODUCTOS", "PERFIL"])
        with t1:
            mis_p = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            with st.expander("SUBIR VIDEO"):
                with st.form("add"):
                    n = st.text_input("Nombre"); pr = st.number_input("Precio"); vi = st.file_uploader("MP4", type=['mp4'])
                    if st.form_submit_button("SUBIR"):
                        path = f"v/{random.randint(10,99)}.mp4"
                        supabase.storage.from_("fotos_productos").upload(path, vi.getvalue())
                        url = supabase.storage.from_("fotos_productos").get_public_url(path)
                        supabase.table("productos").insert({"nombre_producto":n,"precio":pr,"video_url":url,"comercio_relacionado":perf['nombre_comercio']}).execute()
                        st.rerun()
            for mp in mis_p:
                st.write(f"{mp['nombre_producto']} - ${mp['precio']}")
                if st.button("ELIMINAR", key=f"d_{mp['id']}"):
                    supabase.table("productos").delete().eq("id", mp['id']).execute(); st.rerun()