import streamlit as st
from supabase import create_client, Client
import urllib.parse

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
# 2. ESTÉTICA LUXURY (CSS FINAL)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000000; color: #ffffff; }
    
    /* CÍRCULOS DE PORTADA XL (200px) */
    .img-redonda {
        width: 200px; height: 200px; border-radius: 50%;
        object-fit: cover; border: 3px solid #D4AF37;
        margin: 0 auto 15px auto; display: block;
        box-shadow: 0px 10px 25px rgba(212, 175, 55, 0.2);
    }

    /* BOTÓN COMPRAR (DORADO) */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 12px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
        height: 50px !important; width: 100% !important;
    }

    /* BOTÓN REGRESAR DELGADO */
    .btn-regresar button {
        background: transparent !important; color: #ffffff !important; 
        border: 1px solid rgba(255,255,255,0.3) !important;
        height: 32px !important; font-size: 0.75rem !important;
        margin-top: 5px !important;
    }

    /* ESTILO PARA EL NOMBRE Y PRECIO JUNTOS */
    .product-title {
        text-align: center;
        color: #D4AF37;
        font-size: 1.5rem;
        margin-top: 10px;
    }
    .product-price {
        color: #39FF14;
        font-weight: 800;
        margin-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DEL CARRITO
# ==========================================
@st.dialog("💎 PROCESAR COMPRA")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    st.write(f"Vendedor: **{tienda['nombre_comercio']}**")
    
    col1, col2 = st.columns(2)
    with col1:
        cantidad = st.number_input("Cantidad", min_value=1, value=1)
    with col2:
        total = float(producto['precio']) * cantidad
        st.metric("TOTAL", f"${total:,.2f}")
    
    st.divider()
    st.markdown("### 💳 MÉTODOS DE PAGO")
    st.info(tienda.get('datos_pago', 'Contactar al vendedor para detalles de pago.'))
    
    ref = st.text_input("Referencia de Pago")
    
    if st.button("🚀 CONFIRMAR POR WHATSAPP"):
        if ref:
            mensaje = (
                f"✨ *NUEVO PEDIDO*\n\n"
                f"📦 *Producto:* {producto['nombre_producto']}\n"
                f"🔢 *Cantidad:* {cantidad}\n"
                f"💰 *Total:* ${total:,.2f}\n"
                f"🎫 *Referencia:* {ref}"
            )
            tel = str(tienda['whatsapp']).strip().replace("+", "")
            url_wa = f"https://wa.me/{tel}?text={urllib.parse.quote(mensaje)}"
            st.link_button("ABRIR WHATSAPP", url_wa)
        else:
            st.error("Ingresa la referencia.")

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"

# --- VISTA: PANEL DE CONTROL ---
if es_admin:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.container(border=True):
            m = st.text_input("Email").lower()
            c = st.text_input("Código", type="password")
            if st.button("ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
                if res.data and str(res.data[0]['codigo_acceso']).upper() == c.upper():
                    st.session_state.logged_in = True
                    st.session_state.user_email = m
                    st.rerun()
    else:
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        t1, t2, t3 = st.tabs(["📦 PRODUCTOS", "🖼️ PORTADA", "💳 PAGOS"])
        
        with t1:
            c_res = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            actual = c_res.count if c_res.count else 0
            limite = PLANES.get(perf['plan'], 3)
            st.write(f"Cupos: **{actual} / {limite}**")
            
            if actual < limite:
                with st.expander("➕ SUBIR PRODUCTO"):
                    with st.form("add_p", clear_on_submit=True):
                        np = st.text_input("Nombre")
                        pp = st.number_input("Precio ($)")
                        vp = st.file_uploader("Video MP4", type=['mp4'])
                        if st.form_submit_button("SUBIR"):
                            # Aquí va tu lógica de storage y insert
                            st.success("Subido exitosamente")
            
            st.subheader("Tu Inventario")
            prods_m = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            for mp in prods_m:
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"🎥 {mp['nombre_producto']} - ${mp['precio']}")
                if col_b.button("🗑️", key=f"del_{mp['id']}"):
                    supabase.table("productos").delete().eq("id", mp['id']).execute()
                    st.rerun()

        with t2:
            st.subheader("Foto de Portada")
            if perf['portada_url']: st.image(perf['portada_url'], width=150)
            nueva_p = st.file_uploader("Nueva Portada", type=['jpg', 'png'])
            if st.button("GUARDAR FOTO"):
                st.success("Foto actualizada")

        with t3:
            st.subheader("Datos de Pago")
            datos = st.text_area("Instrucciones de pago para el cliente", value=perf.get('datos_pago', ''))
            if st.button("ACTUALIZAR DATOS"):
                supabase.table("perfiles_comercio").update({"datos_pago": datos}).eq("id", perf['id']).execute()
                st.success("Guardado")

# --- VISTA: MALL ---
elif st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    tiendas = supabase.table("perfiles_comercio").select("*").execute().data
    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(tiendas):
                t = tiendas[i + j]
                with cols[j]:
                    st.markdown(f'<img src="{t["portada_url"]}" class="img-redonda">', unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align:center; font-weight:bold;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                    if st.button("ENTRAR", key=f"btn_t_{t['id']}", use_container_width=True):
                        st.session_state.tienda_actual = t
                        ir_a('tienda')

# --- VISTA: TIENDA ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    st.markdown('<div class="btn-regresar">', unsafe_allow_html=True)
    if st.button("⬅️ REGRESAR AL MALL"): ir_a('mall')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    for p in prods:
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        
        # PRECIO AL LADO DEL NOMBRE
        st.markdown(f'''
            <div class="product-title">
                {p['nombre_producto'].upper()} 
                <span class="product-price">${p['precio']}</span>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.button(f"🛒 COMPRAR AHORA", key=f"p_{p['id']}", use_container_width=True):
            ventana_pago(p, t)
        st.divider()