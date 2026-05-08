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

PLANES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}

# Inicialización de estados críticos
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

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
        object-fit: cover; border: 3px solid #D4AF37; margin: 0 auto 10px auto; display: block;
    }
    .price-bubble {
        position: absolute; top: 10px; right: 10px;
        background: rgba(0, 0, 0, 0.9); color: #39FF14; 
        padding: 5px 15px; border-radius: 50px; font-weight: 900; border: 2px solid #39FF14;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. NAVEGACIÓN PRINCIPAL
# ==========================================
es_admin = st.query_params.get("admin") == "true"

if not es_admin:
    # --- VISTA PÚBLICA (MALL) ---
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        tiendas = supabase.table("perfiles_comercio").select("*").execute().data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.markdown(f'<img src="{t.get("portada_url")}" class="img-redonda">', unsafe_allow_html=True)
                        if st.button(t['nombre_comercio'].upper(), key=f"mall_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        st.button("⬅️ VOLVER", on_click=lambda: ir_a('mall'))
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        for p in prods:
            with st.container():
                st.markdown(f"<div style='position: relative;'><div class='price-bubble'>${p['precio']}</div></div>", unsafe_allow_html=True)
                st.video(p['video_url'], autoplay=True, loop=True, muted=True)
                st.divider()

else:
    # --- PANEL ADMINISTRATIVO ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        with st.container(border=True):
            m = st.text_input("Email de socio").lower()
            c = st.text_input("Código de acceso", type="password").upper()
            if st.button("🔓 ENTRAR AL PANEL"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == c:
                    st.session_state.logged_in = True
                    st.session_state.user_email = m
                    st.rerun()
                else: st.error("Credenciales incorrectas")
    else:
        # Cargamos los datos del perfil actual
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        
        tab_add, tab_gest, tab_cfg = st.tabs(["➕ PUBLICAR", "📦 GESTIÓN", "🚪 SALIR"])

        with tab_add:
            st.subheader("Subir nuevo producto")
            with st.form("nuevo_produc", clear_on_submit=True):
                nom = st.text_input("Nombre")
                pre = st.number_input("Precio ($)", min_value=0.0)
                vid = st.file_uploader("Video MP4", type=['mp4'])
                if st.form_submit_button("🚀 PUBLICAR AHORA"):
                    if nom and vid:
                        fname = f"v/{random.randint(1000,9999)}.mp4"
                        supabase.storage.from_("fotos_productos").upload(fname, vid.getvalue(), {"content-type": "video/mp4"})
                        v_url = supabase.storage.from_("fotos_productos").get_public_url(fname)
                        supabase.table("productos").insert({
                            "nombre_producto": nom, "precio": pre, 
                            "video_url": v_url, "comercio_relacionado": perf['nombre_comercio']
                        }).execute()
                        st.success("¡Producto publicado con éxito!")
                        st.rerun()

        with tab_gest:
            st.subheader("Administrar mi inventario")
            # Forzamos la lectura fresca de la base de datos en cada carga
            mis_productos = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            
            if not mis_productos:
                st.info("Aún no tienes productos publicados.")
            
            for item in mis_productos:
                with st.container(border=True):
                    # Formulario de edición rápida
                    edit_nombre = st.text_input("Nombre", value=item['nombre_producto'], key=f"n_{item['id']}")
                    edit_precio = st.number_input("Precio", value=float(item['precio']), key=f"p_{item['id']}")
                    
                    c_save, c_del = st.columns(2)
                    
                    # BOTÓN DE GUARDAR
                    if c_save.button("💾 GUARDAR", key=f"btn_save_{item['id']}", use_container_width=True):
                        supabase.table("productos").update({
                            "nombre_producto": edit_nombre, 
                            "precio": edit_precio
                        }).eq("id", item['id']).execute()
                        st.toast("¡Cambios guardados!")
                        st.rerun()

                    # BOTÓN DE BORRAR (EL QUE "SÍ" FUNCIONA)
                    if c_del.button("🗑️ ELIMINAR", key=f"btn_del_{item['id']}", use_container_width=True):
                        # Acción 1: Borrar de la base de datos
                        supabase.table("productos").delete().eq("id", item['id']).execute()
                        # Acción 2: Notificación visual
                        st.toast(f"Eliminado: {item['nombre_producto']}")
                        # Acción 3: El truco final - Limpiar caché y recargar
                        st.rerun()

        with tab_cfg:
            if st.button("CERRAR SESIÓN"):
                st.session_state.logged_in = False
                st.rerun()