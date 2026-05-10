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

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS: PORTADAS CUADRADAS + TIKTOK VIBE
# ==========================================
st.markdown("""
    <style>
    .main { background: #000; color: #fff; }
    .img-cuadrada { width: 100%; aspect-ratio: 1/1; object-fit: cover; margin-bottom: 10px; }
    
    .video-wrapper { 
        position: relative; width: 100%; max-width: 400px; 
        margin: auto; border-radius: 20px; overflow: hidden; 
        border: 1px solid #333;
    }
    
    .video-overlay {
        position: absolute; bottom: 0; left: 0; width: 100%;
        padding: 40px 15px 20px;
        background: linear-gradient(transparent, rgba(0,0,0,0.9));
        z-index: 10; pointer-events: none;
    }

    .price-tag { color: #39FF14; font-weight: 900; font-size: 1.3rem; }
    .product-name { color: #D4AF37; font-weight: 700; text-transform: uppercase; }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #8A6E2F) !important;
        color: #000 !important; font-weight: 800; border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. VISTA: MALL (TIENDAS)
# ==========================================
if st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    
    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(tiendas):
                t = tiendas[i+j]
                with cols[j]:
                    st.markdown(f'<img src="{t["portada_url"]}" class="img-cuadrada">', unsafe_allow_html=True)
                    if st.button(f"ENTRAR A {t['nombre_comercio'].upper()}", key=f"t_{t['id']}", use_container_width=True):
                        st.session_state.tienda_actual = t
                        ir_a('tienda')

# ==========================================
# 4. VISTA: TIENDA (PRODUCTOS)
# ==========================================
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.button("⬅️ VOLVER AL MALL", on_click=lambda: ir_a('mall'))
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        st.markdown(f'''
            <div class="video-wrapper">
                <div class="video-overlay">
                    <div class="product-name">{p['nombre_producto']}</div>
                    <div class="price-tag">${p['precio']}</div>
                </div>
        ''', unsafe_allow_html=True)
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}", use_container_width=True):
            # Lógica de WhatsApp integrada
            msj = f"Hola {t['nombre_comercio']}, quiero el producto: {p['nombre_producto']}"
            st.link_button("CONTACTAR VENDEDOR", f"https://wa.me/{t['whatsapp']}?text={urllib.parse.quote(msj)}")
        st.divider()

# ==========================================
# 5. VISTA: PANEL ADMIN (GESTIÓN REAL)
# ==========================================
elif st.query_params.get("admin") == "true":
    st.title("⚙️ GESTIÓN DE SOCIO")
    
    if not st.session_state.logged_in:
        email = st.text_input("Email registrado")
        pin = st.text_input("PIN de acceso", type="password")
        if st.button("ACCEDER"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email.lower()).execute()
            if res.data and str(res.data[0]['codigo_acceso']) == pin:
                st.session_state.logged_in = True
                st.session_state.user_data = res.data[0]
                st.rerun()
    else:
        user = st.session_state.user_data
        st.success(f"Tienda: {user['nombre_comercio']} | Plan: {user['plan']}")
        
        # --- SUBIR PRODUCTOS CON LÍMITE DE PLAN ---
        actuales = supabase.table("productos").select("*", count="exact").eq("comercio_relacionado", user['nombre_comercio']).execute()
        conteo = actuales.count
        limite = PLANES.get(user['plan'], 3)

        with st.expander("➕ SUBIR NUEVO PRODUCTO"):
            if conteo < limite:
                with st.form("nuevo_p"):
                    n_p = st.text_input("Nombre del producto")
                    p_p = st.number_input("Precio ($)", min_value=0.0)
                    v_p = st.file_uploader("Video (MP4)", type=['mp4'])
                    if st.form_submit_button("PUBLICAR"):
                        # Aquí iría el upload a storage y el insert a tabla
                        st.info("Subiendo...")
            else:
                st.warning(f"Has alcanzado el límite de tu plan ({limite} productos).")

        # --- GESTIÓN DE PRODUCTOS EXISTENTES ---
        st.subheader("Tus Productos")
        for p in actuales.data:
            c1, c2 = st.columns([3, 1])
            c1.write(f"📦 {p['nombre_producto']} - ${p['precio']}")
            if c2.button("🗑️", key=f"del_{p['id']}"):
                supabase.table("productos").delete().eq("id", p['id']).execute()
                st.rerun()