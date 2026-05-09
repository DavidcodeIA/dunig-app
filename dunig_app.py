import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import time

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

@st.cache_resource 
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

supabase = init_connection()

def obtener_cuentas_admin():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "cuentas_activacion").execute()
        return res.data[0]['valor'] if res.data else "⚠️ Cuentas de activación no configuradas."
    except:
        return "❌ Error al conectar con los ajustes del sistema."

# Constantes del Sistema
PLANES_LIMITES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}
OPCIONES_PLAN_VISUAL = {
    "GRATUITO": "⚪ GRATUITO (Básico - 3 Productos)",
    "BRONCE": "🥉 BRONCE (Emprendedor - 10 Productos)",
    "PLATA": "🥈 PLATA (Crecimiento - 25 Productos)",
    "ORO": "👑 ORO (Ilimitado - Ventas Premium)"
}

# Estado de la Sesión
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None
if 'registered' not in st.session_state: st.session_state.registered = False

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
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
    }
    .img-mall-luxury {
        width: 100%; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 25px;
        border: 2px solid #D4AF37; box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.3); margin-bottom: 10px;
    }
    .price-bubble {
        position: absolute; top: 15px; right: 15px;
        background: rgba(0, 0, 0, 0.85); color: #39FF14; 
        padding: 5px 15px; border-radius: 50px;
        font-weight: 900; border: 2px solid #39FF14; z-index: 10;
    }
    .welcome-card {
        background: rgba(0,0,0,0.7); padding: 30px; border-radius: 20px;
        border: 2px solid #D4AF37; text-align: center; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS DE INTERFAZ
# ==========================================
@st.dialog("💎 CARRITO D'UNIG LUXURY")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **DATOS DE PAGO:**\n{tienda.get('datos_pago', 'Consultar al vendedor')}")
    ref = st.text_input("Ingrese Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Producto:* {producto['nombre_producto']}\n🔢 *Cant:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("ENVIAR POR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else:
            st.error("Por favor, ingrese la referencia de pago")

@st.dialog("📝 GESTIONAR SOCIO")
def editar_comercio_dialog(comercio):
    nuevo_w = st.text_input("WhatsApp", value=comercio.get('whatsapp', ''))
    nuevo_p = st.selectbox("Plan", options=list(PLANES_LIMITES.keys()), index=list(PLANES_LIMITES.keys()).index(comercio.get('plan', 'GRATUITO')))
    nuevo_a = st.toggle("Activo en Mall", value=comercio.get('activo', False))
    if st.button("GUARDAR CAMBIOS"):
        supabase.table("perfiles_comercio").update({"whatsapp": nuevo_w, "plan": nuevo_p, "activo": nuevo_a}).eq("id", comercio['id']).execute()
        st.rerun()

# ==========================================
# 4. LÓGICA DE NAVEGACIÓN
# ==========================================
es_admin_master = st.query_params.get("admin") == "true"
es_via_register = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO ---
if es_via_register:
    if st.session_state.registered:
        st.balloons()
        st.markdown(f"""
            <div class='welcome-card'>
                <h1 style='color: #D4AF37; font-size: 2.2rem; line-height: 1.2;'>
                    BIENVENIDOS A D'UNIG LUXURY <br>
                    <span style='font-size: 1.5rem; color: #FFFFFF;'>tu mejor aliado comercial</span>
                </h1>
                <hr style='border: 0.5px solid #D4AF37; width: 60%; margin: 20px auto;'>
                <div style='padding: 0 10px; text-align: center;'>
                    <p style='font-size: 1.2rem; color: #f0f0f0;'>
                        En el transcurso del día se <b>activará tu plan</b> y se te entregará 
                        tu <b>código de ingreso</b> a través del número de WhatsApp que ingresaste.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.write("")
        st.link_button("🚀 IR AL PANEL DE CONTROL", "https://dunig-app-luxury-v2.streamlit.app/?admin=true", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align:center;