import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def obtener_cuentas_admin():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "cuentas_activacion").execute()
        return res.data[0]['valor'] if res.data else "⚠️ Cuentas de activación no configuradas."
    except:
        return "❌ Error al conectar con los ajustes del sistema."

PLANES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}

OPCIONES_PLAN_VISUAL = {
    "GRATUITO": "⚪ GRATUITO (Básico - 3 Productos)",
    "BRONCE": "🥉 BRONCE (Emprendedor - 10 Productos)",
    "PLATA": "🥈 PLATA (Crecimiento - 25 Productos)",
    "ORO": "👑 ORO (Ilimitado - Ventas Premium)"
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS ACTUALIZADO A 3 COLUMNAS)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    
    /* Forzar 3 Columnas compactas */
    [data-testid="stHorizontalBlock"] { gap: 8px !important; }

    /* Portadas RECTANGULARES VERTICALES con esquinas OVALADAS */
    .img-mall-luxury {
        width: 100%;
        aspect-ratio: 2 / 3; 
        object-fit: cover;
        border-radius: 18px; 
        border: 1px solid #D4AF37;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }

    .tienda-nombre-mall {
        color: #D4AF37;
        font-size: 0.65rem;
        font-weight: bold;
        text-align: center;
        margin-top: 5px;
        text-transform: uppercase;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Botones Dorados Luxury Pequeños */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #8A6E2F) !important;
        color: #000 !important; border-radius: 20px !important;
        font-weight: 700 !important; font-size: 10px !important;
        text-transform: uppercase; border: none !important;
        height: 25px !important;
    }

    .price-bubble {
        position: absolute; top: 15px; right: 15px;
        background: rgba(0, 0, 0, 0.85); color: #39FF14; 
        padding: 5px 15px; border-radius: 50px;
        font-weight: 900; border: 2px solid #39FF14; z-index: 10;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO ---
if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO</h1>", unsafe_allow_html=True)
    with st.form("form_reg_externo", clear_on_submit=True):
        rn = st.text_input("Nombre de la Tienda")
        rm = st.text_input("Email").lower()
        rt = st.text_input("WhatsApp")
        plan_sel = st.selectbox("Plan", options=list(PLANES.keys()))
        ri = st.file_uploader("Foto de Portada", type=['jpg', 'png'])
        if st.form_submit_button("REGISTRAR"):
            if rn and ri:
                path_i = f"portadas/reg_{random.randint(1000,9999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path_i, ri.getvalue())
                url_i = supabase.storage.from_("fotos_productos").get_public_url(path_i)
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": rn, "email_propietario": rm, "whatsapp": rt, 
                    "portada_url": url_i, "plan": plan_sel, "codigo_acceso": f"{random.randint(1000,9999)}"
                }).execute()
                st.success("Registrado correctamente.")

# --- VISTA: MALL (3 CUADROS POR FILA) ---
elif not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h2 style='text-align:center; color:#D4AF37;'>D'UNIG LUXURY MALL</h2>", unsafe_allow_html=True)
        tiendas = supabase.table("perfiles_comercio").select("*").execute().data
        
        for i in range(0, len(tiendas), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.markdown(f'<img src="{t.get("portada_url")}" class="img-mall-luxury">', unsafe_allow_html=True)
                        st.markdown(f'<div class="tienda-nombre-mall">{t["nombre_comercio"]}</div>', unsafe_allow_html=True)
                        if st.button("ENTRAR", key=f"m_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER"): ir_a('mall')
        st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        for p in prods:
            with st.container(border=True):
                st.video(p['video_url'])
                st.write(f"**{p['nombre_producto']}** - ${p['precio']}")
                if st.button(f"🛒 COMPRAR", key=f"btn_{p['id']}", use_container_width=True):
                    tel = str(t['whatsapp']).replace("+", "").strip()
                    msj = f"Hola, me interesa {p['nombre_producto']}"
                    st.link_button("WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")

# --- VISTA: SUPER ADMIN O PANEL SOCIO ---
else:
    # SI ES ADMIN GENERAL (TÚ)
    if es_admin and not st.session_state.logged_in:
        st.markdown("<h2 style='text-align:center; color:#D4AF37;'>👑 MASTER ADMIN</h2>", unsafe_allow_html=True)
        tiendas_master = supabase.table("perfiles_comercio").select("*").execute().data
        for tm in tiendas_master:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 3, 1])
                c1.image(tm['portada_url'], width=50)
                c2.write(f"**{tm['nombre_comercio']}** ({tm['plan']})")
                if c3.button("🗑️", key=f"master_del_{tm['id']}"):
                    # Esto funciona por el CASCADE que configuraste en SQL
                    supabase.table("perfiles_comercio").delete().eq("id", tm['id']).execute()
                    st.rerun()
    
    # PANEL DE SOCIO NORMAL
    else:
        st.markdown("<h2 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h2>", unsafe_allow_html=True)
        if not st.session_state.logged_in:
            m = st.text_input("Email").lower()
            c = st.text_input("Código", type="password")
            if st.button("ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
                if res.data and str(res.data[0]['codigo_acceso']) == c:
                    st.session_state.logged_in = True; st.session_state.user_email = m; st.rerun()
        else:
            perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
            t1, t2 = st.tabs(["➕ PRODUCTOS", "📦 GESTIÓN"])
            with t1:
                with st.form("add"):
                    n = st.text_input("Producto")
                    p = st.number_input("Precio")
                    v = st.file_uploader("Video", type=['mp4'])
                    if st.form_submit_button("SUBIR"):
                        fname = f"v/{random.randint(1000,9999)}.mp4"
                        supabase.storage.from_("fotos_productos").upload(fname, v.getvalue())
                        vurl = supabase.storage.from_("fotos_productos").get_public_url(fname)
                        supabase.table("productos").insert({"nombre_producto":n, "precio":p, "video_url":vurl, "comercio_relacionado":perf['nombre_comercio']}).execute()
                        st.rerun()
            with t2:
                if st.button("CERRAR SESIÓN"):
                    st.session_state.logged_in = False; st.rerun()