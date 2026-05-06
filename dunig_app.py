import streamlit as st
from supabase import create_client, Client
import random
import string
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN INICIAL Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# --- Funciones de Apoyo ---
def generar_codigo():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

# --- Estado de la Sesión ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# --- Estética Luxury ---
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: white; }
    .stButton>button { 
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295); 
        color: black !important; border-radius: 30px; font-weight: 800; border: none; width: 100%;
    }
    .luxury-card { 
        background: rgba(255,255,255,0.05); border: 1px solid #D4AF37; 
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA DE NAVEGACIÓN (ADMIN vs MALL)
# ==========================================
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL D'UNIG</h1>", unsafe_allow_html=True)
    
    # --- PANTALLA DE LOGIN ---
    if not st.session_state.logged_in:
        st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)
        
        with col_a:
            email_log = st.text_input("Email Registrado").strip().lower()
        with col_b:
            pass_log = st.text_input("Código de Acceso", type="password").strip().upper()
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔓 ENTRAR AL PANEL"):
                if email_log and pass_log:
                    res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_log).execute()
                    if res.data:
                        user = res.data[0]
                        if str(user.get('codigo_acceso')).strip().upper() == pass_log:
                            st.session_state.logged_in = True
                            st.session_state.user_email = email_log
                            st.rerun()
                        else: st.error("Código incorrecto.")
                    else: st.error("Email no encontrado.")
        
        with c2:
            if st.button("🔑 SOLICITAR LLAVE (WA)"):
                if email_log:
                    res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_log).execute()
                    if res.data:
                        user = res.data[0]
                        cod = user.get('codigo_acceso') or generar_codigo()
                        if not user.get('codigo_acceso'):
                            supabase.table("perfiles_comercio").update({"codigo_acceso": cod}).eq("id", user['id']).execute()
                        
                        tel = str(user.get('whatsapp', '')).replace("+", "").strip()
                        msg = urllib.parse.quote(f"*D'UNIG LUXURY*\nTu llave de acceso es: *{cod}*")
                        st.link_button("🟢 RECIBIR EN WHATSAPP", f"https://wa.me/{tel}?text={msg}")
                    else: st.error("Email no registrado.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- PANEL DE ADMINISTRACIÓN ACTIVO ---
    else:
        st.sidebar.success(f"Conectado como: {st.session_state.user_email}")
        if st.sidebar.button("🚪 CERRAR SESIÓN"):
            st.session_state.logged_in = False
            st.rerun()

        tab1, tab2 = st.tabs(["📦 Gestión de Inventario", "🎨 Mi Perfil"])

        with tab1:
            st.subheader("Registrar Nuevo Producto")
            with st.form("form_prod", clear_on_submit=True):
                n = st.text_input("Nombre del Producto")
                p = st.number_input("Precio ($)", min_value=0.0)
                desc = st.text_area("Descripción")
                if st.form_submit_button("💾 GUARDAR EN INVENTARIO"):
                    if n:
                        data = {"nombre": n, "precio": p, "descripcion": desc, "vendedor_email": st.session_state.user_email}
                        supabase.table("productos").insert(data).execute()
                        st.success("¡Producto añadido con éxito!")
                        st.rerun()

            st.divider()
            st.subheader("Tu Inventario Actual")
            prods = supabase.table("productos").select("*").eq("vendedor_email", st.session_state.user_email).execute()
            if prods.data:
                for item in prods.data:
                    with st.expander(f"🔹 {item['nombre']} - ${item['precio']}"):
                        st.write(item['descripcion'])
                        if st.button(f"🗑️ Eliminar {item['id']}", key=item['id']):
                            supabase.table("productos").delete().eq("id", item['id']).execute()
                            st.rerun()
            else:
                st.info("No tienes productos cargados.")

        with tab2:
            st.info("Configuración de perfil y logo próximamente.")

else:
    # --- VISTA PÚBLICA (MALL) ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG PLATINUM MALL</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>La vitrina de lujo más exclusiva.</p>", unsafe_allow_html=True)
    
    # Mostrar productos de todos los vendedores
    todos = supabase.table("productos").select("*").execute()
    if todos.data:
        cols = st.columns(3)
        for idx, p in enumerate(todos.data):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class='luxury-card'>
                    <h3 style='color:#D4AF37;'>{p['nombre']}</h3>
                    <p><b>Precio:</b> ${p['precio']}</p>
                    <button style='width:100%; border-radius:10px;'>Ver Detalles</button>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("El Mall está abriendo sus puertas. Vuelve pronto.")
