import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import string

# ==========================================
# 1. CONEXIÓN Y CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Límites de inventario según el plan
PLANES_LIMITES = {"BRONCE": 3, "PLATINUM": 15, "DIAMANTE": 50}

def generar_codigo_fijo():
    # Genera una combinación única de 7 caracteres (Letras y Números)
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

# --- ESTÉTICA LUXURY ---
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: white; }
    .stButton>button { 
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295); 
        color: black !important; border-radius: 30px; font-weight: 800; border: none; width: 100%;
    }
    .luxury-card { 
        background: rgba(255,255,255,0.03); border: 1px solid rgba(212,175,55,0.2); 
        border-radius: 20px; padding: 20px; margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. PANEL DE CONTROL (LÓGICA CORREGIDA)
# ==========================================
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL LUXURY</h1>", unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
        st.subheader("🔑 Acceso Propietario")
        
        # Usamos campos de texto fuera de un 'st.form' para evitar bloqueos de refresco
        email_input = st.text_input("Email Registrado", placeholder="ejemplo@correo.com").lower().strip()
        pass_input = st.text_input("Tu Código Luxury (7 caracteres)", type="password", placeholder="Ingresa tu llave").upper().strip()
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔓 INGRESAR"):
                if email_input and pass_input:
                    # Consulta directa a Supabase para verificar credenciales
                    res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_input).execute()
                    if res.data:
                        user = res.data[0]
                        # Verificamos si el código coincide exactamente
                        if user.get('codigo_acceso') == pass_input:
                            st.session_state.logged_in = True
                            st.session_state.user_email = email_input
                            st.success("Acceso verificado. Entrando...")
                            st.rerun()
                        else:
                            st.error("El código ingresado es incorrecto.")
                    else:
                        st.error("Este email no está registrado.")
                else:
                    st.warning("Por favor, rellena ambos campos.")

        with col2:
            if st.button("✨ CREAR / VER MI CÓDIGO"):
                if email_input:
                    res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_input).execute()
                    if res.data:
                        user = res.data[0]
                        cod_db = user.get('codigo_acceso')
                        
                        if not cod_db:
                            # Si no tiene código, lo creamos y guardamos permanentemente
                            nuevo_c = generar_codigo_fijo()
                            supabase.table("perfiles_comercio").update({"codigo_acceso": nuevo_c}).eq("id", user['id']).execute()
                            st.success(f"¡Código Creado! Tu llave permanente es: {nuevo_c}")
                        else:
                            # Si ya tiene uno, se lo recordamos
                            st.info(f"Tu código asignado es: {cod_db}")
                    else:
                        st.error("Email no encontrado en la base de datos.")
                else:
                    st.warning("Escribe tu email primero.")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # --- PANEL DE GESTIÓN INTERNO ---
        res_p = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        if res_p.data:
            perf = res_p.data[0]
            plan = perf.get('plan', 'BRONCE').upper()
            
            if plan == "BRONCE":
                st.warning("⚠️ TIENDA OCULTA: Tu tienda no es visible en el Mall. Activa un plan para atraer clientes.")
            
            # Navegación interna del Admin
            tabs = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS", "💎 MI PLAN"])
            
            with tabs[0]: # Agregar Productos
                limite = PLANES_LIMITES.get(plan, 3)
                st.write(f"Cupos disponibles: {limite} productos.")
                # Lógica de subida aquí...

            with tabs[3]: # Mi Plan y Reporte de Pago
                st.markdown("### 🏆 Gestión de Membresía")
                st.write("Reporta tu pago para habilitar más productos y aparecer en el Mall.")
                ref_pago = st.text_input("Referencia de la transacción")
                if st.button("REPORTAR PAGO AL GMAIL"):
                    if ref_pago:
                        asunto = f"PAGO_LUXURY_{perf['nombre_comercio']}"
                        cuerpo = f"Comercio: {perf['nombre_comercio']}%0AReferencia: {ref_pago}"
                        st.link_button("📩 ENVIAR CORREO", f"mailto:idealiting@gmail.com?subject={asunto}&body={cuerpo}")

        if st.sidebar.button("CERRAR SESIÓN"):
            st.session_state.logged_in = False
            st.rerun()

else:
    # --- MALL PÚBLICO ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    # Solo mostramos tiendas que NO están en plan Bronce
    res_m = supabase.table("perfiles_comercio").select("*").neq("plan", "BRONCE").execute()
    if res_m.data:
        for t in res_m.data:
            st.markdown(f"<div class='luxury-card'><h3>{t['nombre_comercio'].upper()}</h3></div>", unsafe_allow_html=True)
    else:
        st.info("Mall exclusivo. Las tiendas aparecerán una vez activen su plan.")
