import streamlit as st
from supabase import create_client, Client
import urllib.parse

# Configuración de lujo
st.set_page_config(page_title="D'UNIG PLATINUM", layout="centered")

# Conexión
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ESTILO TIKTOK SHOP ---
st.markdown("""
    <style>
    .main { background-color: #000000; }
    .video-card {
        border: 2px solid #D4AF37;
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 20px;
        background: #111;
    }
    .buy-btn {
        background: linear-gradient(90deg, #D4AF37, #8B6B1E);
        color: white;
        font-weight: bold;
        width: 100%;
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        display: block;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN ---
if 'view' not in st.session_state: st.session_state.view = 'mall'

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# --- VISTA: CENTRO COMERCIAL ---
if st.session_state.view == 'mall':
    st.image("https://jbtscidofkofclhuxeyf.supabase.co/storage/v1/object/public/fotos_productos/logos/logo_oficial.jpg", width=200)
    st.title("⚜️ D'UNIG PLATINUM")
    
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    
    for t in tiendas.data:
        with st.container():
            st.markdown(f"### 🏬 {t['nombre_comercio']}")
            if st.button(f"Entrar a {t['nombre_comercio']}", key=t['id']):
                st.session_state.tienda_actual = t
                ir_a('tienda')

# --- VISTA: TIENDA (TIKTOK STYLE) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.header(f"✨ {t['nombre_comercio']}")
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
    
    if not prods.data:
        st.info("Esta tienda aún no tiene videos.")
    
    for p in prods.data:
        with st.container():
            st.markdown('<div class="video-card">', unsafe_allow_html=True)
            st.video(p['video_url'])
            st.subheader(p['nombre_producto'])
            st.write(f"💎 Precio: ${p['precio']}")
            
            # Botón de Checkout Directo a WhatsApp
            msg = f"Hola {t['nombre_comercio']}, me interesa el producto {p['nombre_producto']} de D'UNIG PLATINUM."
            msg_encoded = urllib.parse.quote(msg)
            ws_url = f"https://wa.me/{t['whatsapp']}?text={msg_encoded}"
            
            st.markdown(f'<a href="{ws_url}" class="buy-btn">🛍️ COMPRAR AHORA</a>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🔙 Volver al Mall"): ir_a('mall')
