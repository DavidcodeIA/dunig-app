import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import uuid

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

PLANES = {
    "GRATUITO": 3,
    "BRONCE": 10,
    "PLATA": 25,
    "ORO": 100
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS ACTUALIZADO)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000000; color: #ffffff; }
    
    /* CONTENEDOR DE VIDEO RELATIVO */
    .video-container {
        position: relative;
        width: 100%;
        line-height: 0;
    }

    /* BURBUJA DE PRECIO EN LA ESQUINA INFERIOR DERECHA */
    .price-bubble {
        position: absolute;
        bottom: 20px;   /* Ajustado para estar abajo */
        right: 15px;    /* Ajustado para la otra esquina */
        background: rgba(0, 0, 0, 0.7); 
        color: #39FF14; 
        padding: 6px 14px; 
        border-radius: 8px;
        font-weight: 900; 
        border: 1px solid rgba(57, 255, 20, 0.5); 
        z-index: 10;
        font-size: 1.1rem;
        backdrop-filter: blur(5px);
    }

    /* BOTÓN COMPRAR */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 50px !important; width: 100% !important;
    }

    .btn-regresar button {
        background: transparent !important; color: #ffffff !important; 
        border: 1px solid rgba(255,255,255,0.2) !important;
        height: 30px !important; font-size: 0.7rem !important;
        margin-bottom: 10px;
    }

    .img-redonda {
        width: 130px; height: 130px; border-radius: 50%;
        object-fit: cover; border: 2px solid #D4AF37;
        margin: 0 auto 10px auto; display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DEL CARRITO
# ==========================================
@st.dialog("💎 DETALLES DE COMPRA")
def ventana_pago(producto, tienda):
    st.markdown(f"### {producto['nombre_producto']}")
    cant = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cant
    st.write(f"**Total a pagar: ${total:,.2f}**")
    st.divider()
    st.info(f"💳 **DATOS DE PAGO:**\n{tienda.get('datos_pago', 'Consultar al vendedor')}")
    ref = st.text_input("Referencia de Pago")
    if st.button("CONFIRMAR PEDIDO"):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Producto:* {producto['nombre_producto']}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("ENVIAR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else: st.error("Falta la referencia")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"

if not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ LUXURY MALL</h1>", unsafe_allow_html=True)
        tiendas = supabase.table("perfiles_comercio").select("*").execute().data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.markdown(f'<img src="{t["portada_url"]}" class="img-redonda">', unsafe_allow_html=True)
                        if st.button(f"{t['nombre_comercio'].upper()}", key=f"t_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        st.markdown('<div class="btn-regresar">', unsafe_allow_html=True)
        if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
        
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        for p in prods:
            # --- VIDEO CON PRECIO ABAJO A LA DERECHA ---
            st.markdown(f'''
                <div class="video-container">
                    <div class="price-bubble">${p['precio']}</div>
                </div>
            ''', unsafe_allow_html=True)
            
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            
            st.markdown(f"<h3 style='text-align:center;'>{p['nombre_producto']}</h3>", unsafe_allow_html=True)
            if st.button(f"🛒 COMPRAR AHORA", key=f"p_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.divider()

else:
    # --- PANEL ADMIN COMPLETO ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL ADMIN</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        m = st.text_input("Email")
        c = st.text_input("Código", type="password")
        if st.button("ENTRAR"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m.lower()).execute()
            if res.data and str(res.data[0]['codigo_acceso']).upper() == c.upper():
                st.session_state.logged_in = True
                st.session_state.user_email = m
                st.rerun()
    else:
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        tab1, tab2, tab3 = st.tabs(["📦 PRODUCTOS", "🖼️ PERFIL", "💳 COBROS"])
        
        with tab1:
            # Subir productos
            with st.expander("➕ NUEVO PRODUCTO"):
                with st.form("add"):
                    n = st.text_input("Nombre")
                    pr = st.number_input("Precio")
                    v = st.file_uploader("Video", type=['mp4'])
                    if st.form_submit_button("PUBLICAR"):
                        # Lógica de guardado...
                        st.rerun()
            
            # Gestión/Borrar productos (LO QUE FALTABA)
            st.subheader("Tus Productos")
            mis_p = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            for mp in mis_p:
                c1, c2 = st.columns([4, 1])
                c1.write(f"🔹 {mp['nombre_producto']} (${mp['precio']})")
                if c2.button("🗑️", key=f"del_{mp['id']}"):
                    supabase.table("productos").delete().eq("id", mp['id']).execute()
                    st.rerun()

        with tab2:
            st.subheader("Foto de Portada")
            if perf['portada_url']: st.image(perf['portada_url'], width=100)
            nf = st.file_uploader("Cambiar Foto", type=['jpg', 'png'])
            if st.button("GUARDAR PORTADA"):
                # Lógica de actualización...
                st.rerun()

        with tab3:
            st.subheader("Configuración de Pagos")
            dp = st.text_area("Datos de Pago", value=perf.get('datos_pago', ''))
            if st.button("ACTUALIZAR PAGOS"):
                supabase.table("perfiles_comercio").update({"datos_pago": dp}).eq("id", perf['id']).execute()
                st.success("Guardado")