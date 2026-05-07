import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import streamlit.components.v1 as components

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
    "ORO": 9999
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY Y SCRIPT DE AUTOPLAY-SCROLL
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    
    .video-card {
        background: rgba(255,255,255,0.05);
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 40px;
        border: 1px solid rgba(212, 175, 55, 0.3);
        position: relative;
    }
    
    .price-bubble {
        position: absolute; top: 25px; right: 25px;
        background: rgba(0, 0, 0, 0.85); color: #39FF14; 
        padding: 8px 18px; border-radius: 50px;
        font-weight: 900; border: 2px solid #39FF14; z-index: 10;
    }

    video {
        width: 100%;
        border-radius: 15px;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.5);
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 30px !important;
        font-weight: 800 !important; text-transform: uppercase; border: none !important;
    }
    </style>

    <script>
    // Script para manejar el scroll y la reproducción automática
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.6 // El video debe estar al 60% visible para activarse
    };

    const handleIntersect = (entries) => {
        entries.forEach(entry => {
            const video = entry.target;
            if (entry.isIntersecting) {
                video.play().catch(error => console.log("Autoplay bloqueado hasta interacción"));
            } else {
                video.pause();
            }
        });
    };

    // Esperar a que los elementos carguen
    setTimeout(() => {
        const observer = new IntersectionObserver(handleIntersect, observerOptions);
        document.querySelectorAll('video').forEach(video => {
            observer.observe(video);
        });
    }, 1500);
    </script>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS
# ==========================================
@st.dialog("💎 CARRITO D'UNIG LUXURY")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.info(f"💳 **DATOS DE PAGO:**\n{tienda.get('datos_pago', 'Consultar al vendedor')}")
    ref = st.text_input("Ingrese Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Producto:* {producto['nombre_producto']}\n🔢 *Cant:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").replace(" ", "").strip()
            st.link_button("ENVIAR POR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")

@st.dialog("✏️ EDITAR PRODUCTO")
def editar_producto(prod):
    nuevo_nom = st.text_input("Nombre", value=prod['nombre_producto'])
    nuevo_pre = st.number_input("Precio ($)", value=float(prod['precio']))
    if st.button("ACTUALIZAR"):
        supabase.table("productos").update({"nombre_producto": nuevo_nom, "precio": nuevo_pre}).eq("id", prod['id']).execute()
        st.success("¡Actualizado!"); st.rerun()

# ==========================================
# 4. LÓGICA DE VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE NUEVO SOCIO</h1>", unsafe_allow_html=True)
    with st.form("form_reg_externo", clear_on_submit=True):
        rn = st.text_input("Nombre de la Tienda")
        rm = st.text_input("Email del Propietario")
        rt = st.text_input("WhatsApp")
        plan_sel = st.selectbox("Selecciona tu Plan", ["GRATUITO", "BRONCE", "PLATA", "ORO"])
        ri = st.file_uploader("Foto de Portada", type=['jpg', 'png'])
        ref_s = st.text_input("Referencia de Pago")
        if st.form_submit_button("REGISTRAR COMERCIO"):
            if rn and rm and rt and ri and ref_s:
                path_i = f"portadas/reg_{random.randint(1000,9999)}.jpg"
                supabase.storage.from_("fotos_productos").upload(path_i, ri.getvalue())
                url_i = supabase.storage.from_("fotos_productos").get_public_url(path_i)
                supabase.table("perfiles_comercio").insert({"nombre_comercio": rn, "email_propietario": rm.lower(), "whatsapp": rt, "portada_url": url_i, "plan": plan_sel, "codigo_acceso": "LUXURY7"}).execute()
                st.success("¡Registrado!")

elif not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        res = supabase.table("perfiles_comercio").select("*").execute()
        tiendas = res.data
        for t in tiendas:
            with st.container(border=True):
                col1, col2 = st.columns([1, 2])
                with col1:
                    url = t.get('portada_url') or "https://via.placeholder.com/150"
                    st.image(url, use_container_width=True)
                with col2:
                    st.subheader(t['nombre_comercio'].upper())
                    if st.button("VISITAR TIENDA", key=f"m_{t['id']}", use_container_width=True):
                        st.session_state.tienda_actual = t
                        ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        
        for p in prods.data:
            st.markdown(f"""
                <div class="video-card">
                    <div class="price-bubble">${p['precio']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Autoplay y Loop activados. Muted=True para permitir el autoplay del navegador.
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            
            st.markdown(f"<h3 style='text-align:center;'>{p['nombre_producto']}</h3>", unsafe_allow_html=True)
            if st.button(f"🛒 COMPRAR AHORA", key=f"btn_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.divider()

else:
    # --- PANEL ADMIN ---
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    if not st.session_state.logged_in:
        with st.container(border=True):
            m = st.text_input("Email").strip().lower()
            c = st.text_input("Código", type="password").strip().upper()
            if st.button("🔓 ENTRAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", m).execute()
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == c:
                    st.session_state.logged_in = True; st.session_state.user_email = m; st.rerun()
                else: st.error("Acceso denegado")
    else:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        if res.data:
            perf = res.data[0]
            c_res = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perf['nombre_comercio']).execute()
            actual = c_res.count if c_res.count is not None else 0
            limite = PLANES.get(perf.get('plan', 'GRATUITO'), 3)
            
            st.markdown(f"### 📊 Uso: {actual} / {limite}")
            st.progress(min(actual/limite, 1.0))

            t1, t2, t3, t4 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS", "💎 UPGRADE"])
            
            with t1:
                if actual >= limite:
                    st.warning("⚠️ Límite alcanzado.")
                    # Botón que redirige al link externo que pediste
                    st.link_button("🚀 MEJORAR PLAN (UPGRADE)", "https://dunig-app-luxury-v2.streamlit.app/?reg=true", use_container_width=True)
                else:
                    with st.form("form_add", clear_on_submit=True):
                        nom_p = st.text_input("Nombre")
                        pre_p = st.number_input("Precio ($)", min_value=0.0)
                        vid_p = st.file_uploader("Video MP4", type=['mp4'])
                        if st.form_submit_button("PUBLICAR"):
                            path = f"v/{random.randint(1000,9999)}.mp4"
                            supabase.storage.from_("fotos_productos").upload(path, vid_p.getvalue())
                            url_v = supabase.storage.from_("fotos_productos").get_public_url(path)
                            supabase.table("productos").insert({"nombre_producto":nom_p, "precio":pre_p, "video_url":url_v, "comercio_relacionado":perf['nombre_comercio']}).execute()
                            st.rerun()

            with t2:
                prods_gest = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for pg in prods_gest.data:
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.write(f"**{pg['nombre_producto']}**")
                    if c2.button("✏️", key=f"ed_{pg['id']}"): editar_producto(pg)
                    if c3.button("🗑️", key=f"del_{pg['id']}"):
                        supabase.table("productos").delete().eq("id", pg['id']).execute()
                        st.rerun()

            with t3:
                d_p = st.text_area("Datos de Pago", value=perf.get('datos_pago','') or "")
                if st.button("GUARDAR DATOS"):
                    supabase.table("perfiles_comercio").update({"datos_pago": d_p}).eq("id", perf['id']).execute()
                    st.success("Guardado")

            with t4:
                st.info("Para subir de nivel, haz clic en el botón de abajo.")
                st.link_button("💎 IR A PLANES", "https://dunig-app-luxury-v2.streamlit.app/?reg=true", use_container_width=True)

            if st.button("🚪 CERRAR SESIÓN"): st.session_state.logged_in = False; st.rerun()