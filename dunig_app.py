import streamlit as st
from supabase import create_client, Client
import random

# ==========================================
# 1. CONFIGURACIÓN Y ESTILO (PANTALLA COMPLETA)
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY MALL", layout="wide", initial_sidebar_state="collapsed")

# Estilo para que los videos se vean grandes y los botones resalten
st.markdown("""
    <style>
    .stVideo { width: 100% !important; border-radius: 15px; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #D4AF37; color: white; font-weight: bold; }
    .store-card { text-align: center; border: 1px solid #D4AF37; border-radius: 10px; padding: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# ==========================================
# 2. LÓGICA DE NAVEGACIÓN
# ==========================================
# Si no hay tienda seleccionada, mostramos el selector de tiendas
if 'tienda_seleccionada' not in st.session_state:
    st.session_state.tienda_seleccionada = None

es_reg = st.query_params.get("reg") == "true"
es_admin = st.query_params.get("admin") == "true"

# ==========================================
# 3. VISTA: SELECCIÓN DE TIENDAS (EL MALL REAL)
# ==========================================
if not es_reg and not es_admin:
    if st.session_state.tienda_seleccionada is None:
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>💎 D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>Selecciona una tienda para ver sus colecciones</p>", unsafe_allow_html=True)
        
        # Obtenemos las tiendas registradas
        tiendas = supabase.table("perfiles_comercio").select("*").execute()
        
        if tiendas.data:
            cols = st.columns(2)
            for i, tienda in enumerate(tiendas.data):
                with cols[i % 2]:
                    with st.container():
                        # Imagen de portada de la tienda
                        st.image(tienda['portada_url'], use_container_width=True)
                        if st.button(f"Entrar a {tienda['nombre_comercio']}", key=tienda['id']):
                            st.session_state.tienda_seleccionada = tienda
                            st.rerun()
        else:
            st.info("Cargando comercios aliados...")

    # ==========================================
    # 4. VISTA: PRODUCTOS DE LA TIENDA (PANTALLA COMPLETA)
    # ==========================================
    else:
        t = st.session_state.tienda_seleccionada
        st.button("⬅️ Volver al Mall", on_click=lambda: st.session_state.update({"tienda_seleccionada": None}))
        st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
        
        # Traemos productos solo de esta tienda
        res = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        
        if res.data:
            for prod in res.data:
                with st.container(border=True):
                    # Video en formato grande/completo
                    st.video(prod['video_url'], format="video/mp4")
                    
                    col_info, col_btn = st.columns([2, 1])
                    with col_info:
                        st.markdown(f"### {prod['nombre_producto']}")
                        st.markdown(f"**Precio: ${prod['precio']}**")
                    
                    with col_btn:
                        # Botón de compra directo al WhatsApp de la tienda
                        msj = f"Hola {t['nombre_comercio']}, me interesa el producto: {prod['nombre_producto']}"
                        link_wa = f"https://wa.me/{t['whatsapp']}?text={msj.replace(' ', '%20')}"
                        st.markdown(f"""<a href="{link_wa}" target="_blank"><button style="width:100%; height:50px; background-color:#25D366; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">🛍️ COMPRAR</button></a>""", unsafe_allow_html=True)
        else:
            st.warning("Esta tienda aún no tiene videos disponibles.")

# ==========================================
# 5. RESTO DE FUNCIONES (ADMIN Y REGISTRO)
# ==========================================
elif es_reg:
    # (Mantenemos tu lógica de registro con blindaje de datos)
    st.title("Registro de Socios")
    # ... código de registro enviado anteriormente ...

elif es_admin:
    # (Mantenemos tu panel de control para subir videos)
    st.title("Panel de Control")
    # ... código de panel enviado anteriormente ...