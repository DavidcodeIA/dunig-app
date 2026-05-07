import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Diccionario de límites según el plan
LIMITES_PLANES = {
    "GRATUITO": 3,
    "BRONCE": 10,
    "PLATA": 25,
    "ORO": 9999
}

# Manejo de navegación por URL
query_params = st.query_params
view_mode = query_params.get("view", "mall")

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 30px !important;
        font-weight: 800 !important; text-transform: uppercase;
    }
    .img-redonda {
        width: 140px; height: 140px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 10px auto; display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VISTA: REGISTRO INDEPENDIENTE (?view=registro)
# ==========================================
if view_mode == "registro":
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>💎 ÚNETE A D'UNIG LUXURY</h1>", unsafe_allow_html=True)
    st.write("Selecciona un plan y registra tu comercio para empezar a vender.")
    
    with st.form("form_registro_independiente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            rn = st.text_input("Nombre de la Tienda")
            rm = st.text_input("Email del Propietario")
        with col2:
            rt = st.text_input("WhatsApp (Ej: 58412...)")
            plan_sel = st.selectbox("Selecciona tu Plan", ["GRATUITO", "BRONCE", "PLATA", "ORO"])
        
        ri = st.file_uploader("Logo de tu Comercio", type=['jpg', 'png'])
        
        if st.form_submit_button("REGISTRAR Y CREAR TIENDA"):
            if rn and rm and rt and ri:
                path_i = f"portadas/reg_{random.randint(1000,9999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path_i, ri.getvalue(), {"x-upsert": "true"})
                url_i = supabase.storage.from_("fotos_productos").get_public_url(path_i)
                
                # Insertamos con el plan seleccionado
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": rn,
                    "email_propietario": rm.lower(),
                    "whatsapp": rt,
                    "portada_url": url_i,
                    "plan": plan_sel,
                    "codigo_acceso": "LUXURY7"
                }).execute()
                st.success(f"¡Bienvenido {rn}! Ya puedes entrar al Panel de Control con tu email.")
                st.balloons()
            else:
                st.error("Por favor completa todos los campos y carga tu logo.")

# ==========================================
# 4. VISTA: PANEL DE CONTROL (COMERCIOS)
# ==========================================
elif view_mode == "admin":
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.container(border=True):
            m = st.text_input("Email").strip().lower()
            c = st.text_input("Código de Acceso", type="password").strip().upper()
            if st.button("🔓 ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == c:
                    st.session_state.logged_in = True
                    st.session_state.user_email = m
                    st.rerun()
                else: st.error("Acceso denegado")
    else:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        if res.data:
            perf = res.data[0]
            plan_actual = perf.get('plan', 'GRATUITO')
            limite = LIMITES_PLANES.get(plan_actual, 3)
            
            # Contar productos actuales
            prods_res = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            cantidad_actual = prods_res.count if prods_res.count is not None else 0

            st.sidebar.markdown(f"### Plan: {plan_actual}")
            st.sidebar.progress(min(cantidad_actual / limite, 1.0))
            st.sidebar.write(f"Productos: {cantidad_actual} / {limite}")

            tab1, tab2, tab3 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS"])

            with tab1:
                if cantidad_actual < limite:
                    with st.form("add_p", clear_on_submit=True):
                        nom = st.text_input("Producto")
                        pre = st.number_input("Precio")
                        vid = st.file_uploader("Video", type=['mp4'])
                        if st.form_submit_button("PUBLICAR"):
                            path = f"v/{random.randint(100,999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(path, vid.getvalue())
                            url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                            supabase.table("productos").insert({"nombre_producto":nom, "precio":pre, "video_url":url_v, "comercio_relacionado":perf['nombre_comercio']}).execute()
                            st.success("¡Publicado!"); st.rerun()
                else:
                    st.warning(f"Has alcanzado el límite de tu plan {plan_actual}. ¡Sube de plan para publicar más!")

            with tab3:
                d_p = st.text_area("Datos de Pago", value=perf.get('datos_pago','') or "")
                if st.button("GUARDAR"):
                    supabase.table("perfiles_comercio").update({"datos_pago": d_p}).eq("id", perf['id']).execute()
                    st.success("Actualizado")

            if st.button("🚪 SALIR"):
                st.session_state.logged_in = False
                st.rerun()

# ==========================================
# 5. VISTA: MALL (PÚBLICO)
# ==========================================
else:
    # Aquí va tu código del Mall que ya funciona perfectamente...
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    # (Mantén la lógica de visualización de tiendas y el carrito de compras aquí)