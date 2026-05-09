import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    # Asegúrate de tener estas keys en tu archivo .streamlit/secrets.toml
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# Configuración de límites de negocio
PLANES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}

# Inicialización de estados de sesión
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. CSS PROFESIONAL: INMERSIVO Y SIN ESPACIOS
# ==========================================
st.markdown("""
    <style>
    /* Reset de márgenes de Streamlit para efecto Full Screen */
    .block-container { padding: 0rem !important; max-width: 100% !important; }
    .stApp { background-color: #000; }
    header { visibility: hidden; }
    
    /* Contenedor de Video Tipo Reel */
    .video-wrapper {
        position: relative;
        width: 100%;
        aspect-ratio: 9 / 16;
        background: #000;
        overflow: hidden;
        margin-bottom: 0px !important;
    }

    /* Video pegado sin bordes ovalados */
    .stVideo { width: 100% !important; margin: 0 !important; }
    .stVideo video { 
        object-fit: cover !important; 
        border-radius: 0px !important; 
        height: 100% !important;
    }

    /* Overlay: Precio sobre Nombre (Esquina Inferior) */
    .video-overlay-info {
        position: absolute;
        bottom: 40px;
        left: 20px;
        z-index: 99;
        pointer-events: none;
        text-align: left;
    }

    .burbuja-precio {
        background: linear-gradient(135deg, #D4AF37, #F9F295);
        color: #000;
        padding: 4px 12px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.1rem;
        display: inline-block;
        margin-bottom: 5px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.6);
    }

    .nombre-producto {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: 800;
        text-transform: uppercase;
        text-shadow: 2px 2px 8px rgba(0,0,0,1);
        margin: 0;
    }

    /* Botones de Acción (Pegados al video) */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295) !important;
        color: #000 !important;
        border-radius: 0px !important;
        font-weight: 800 !important;
        border: none !important;
        height: 55px;
        width: 100% !important;
        margin: 0 !important;
        text-transform: uppercase;
    }
    
    /* Estilo para las portadas del Mall */
    .img-portada-full {
        width: 100%; aspect-ratio: 1 / 1; object-fit: cover;
        border: 1px solid #D4AF37; margin-bottom: -5px;
    }

    /* Quitar espacios entre widgets */
    div.stVerticalBlock > div { padding: 0px !important; margin: 0px !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. COMPONENTES Y DIÁLOGOS
# ==========================================
@st.dialog("💎 PROCESAR PEDIDO")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.info(f"💳 **MÉTODO DE PAGO:**\n{tienda.get('datos_pago', 'Consultar por WhatsApp')}")
    ref = st.text_input("Referencia de Pago")
    if st.button("🚀 CONFIRMAR Y ENVIAR"):
        if ref:
            msj = f"✨ *PEDIDO D'UNIG*\n📦 *Producto:* {producto['nombre_producto']}\n🔢 *Cant:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).strip()
            st.link_button("ENVIAR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else: st.error("Falta la referencia")

# ==========================================
# 4. RUTAS Y VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_registro = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO DE SOCIOS ---
if es_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37; padding:20px;'>REGISTRO D'UNIG</h1>", unsafe_allow_html=True)
    with st.form("reg_socio"):
        nombre = st.text_input("Nombre de la Marca")
        correo = st.text_input("Email")
        wsp = st.text_input("WhatsApp (Incluir código país)")
        logo = st.file_uploader("Sube tu Logo (Cuadrado)", type=['jpg', 'png'])
        if st.form_submit_button("REGISTRAR NEGOCIO"):
            if nombre and logo:
                fname = f"logos/{random.randint(100,999)}_{nombre}.jpg"
                supabase.storage.from_("fotos_productos").upload(fname, logo.getvalue())
                url_logo = supabase.storage.from_("fotos_productos").get_public_url(fname)
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": nombre, "email_propietario": correo.lower(),
                    "whatsapp": wsp, "portada_url": url_logo, "plan": "GRATUITO", "codigo_acceso": "LUXURY1"
                }).execute()
                st.success("¡Registro realizado! Entra al modo Admin.")

# --- VISTA: EL MALL (PORTADAS) ---
elif not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37; padding:20px;'>🏙️ D'UNIG MALL</h1>", unsafe_allow_html=True)
        tiendas = supabase.table("perfiles_comercio").select("*").execute().data
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2, gap="small")
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        st.markdown(f'<img src="{t["portada_url"]}" class="img-portada-full">', unsafe_allow_html=True)
                        if st.button(t['nombre_comercio'].upper(), key=f"t_{t['id']}"):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    # --- VISTA: TIENDA (FEED DE VIDEOS) ---
    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
        
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        for p in prods:
            st.markdown(f"""
                <div class="video-wrapper">
                    <div class="video-overlay-info">
                        <div class="burbuja-precio">${p['precio']}</div>
                        <p class="nombre-producto">{p['nombre_producto']}</p>
                    </div>
            """, unsafe_allow_html=True)
            st.video(p['video_url'], autoplay=True, loop=True, muted=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{p['id']}"):
                ventana_pago(p, t)

# --- VISTA: PANEL ADMIN (GESTIÓN TOTAL) ---
else:
    if not st.session_state.logged_in:
        st.markdown("<h2 style='text-align:center;'>ACCESO ADMIN</h2>", unsafe_allow_html=True)
        email_log = st.text_input("Correo").lower()
        pass_log = st.text_input("Código de Acceso", type="password")
        if st.button("INGRESAR"):
            res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", email_log).execute()
            if res.data and str(res.data[0]['codigo_acceso']) == pass_log:
                st.session_state.logged_in = True
                st.session_state.user_email = email_log
                st.rerun()
            else: st.error("Datos incorrectos")
    else:
        # Recuperar perfil del socio logueado
        perfil = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        st.write(f"Bienvenido: **{perfil['nombre_comercio']}** | Plan: {perfil['plan']}")
        
        tab1, tab2 = st.tabs(["📦 MIS PRODUCTOS", "⚙️ MI PERFIL"])
        
        with tab1:
            # Lógica de creación con límites
            mis_prods = supabase.table("productos").select("*").eq("comercio_relacionado", perfil['nombre_comercio']).execute().data
            count = len(mis_prods)
            limite = PLANES.get(perfil['plan'], 3)
            
            st.progress(count/limite, text=f"{count} de {limite} productos usados")
            
            if count < limite:
                with st.expander("➕ SUBIR NUEVO PRODUCTO"):
                    with st.form("new_p"):
                        np = st.text_input("Nombre del Producto")
                        pp = st.number_input("Precio ($)", min_value=0.0)
                        vp = st.file_uploader("Video Vertical (MP4)", type=['mp4'])
                        if st.form_submit_button("SUBIR"):
                            if np and vp:
                                vname = f"videos/{random.randint(100,999)}_{perfil['id']}.mp4"
                                supabase.storage.from_("fotos_productos").upload(vname, vp.getvalue())
                                vurl = supabase.storage.from_("fotos_productos").get_public_url(vname)
                                supabase.table("productos").insert({
                                    "nombre_producto": np, "precio": pp, "video_url": vurl,
                                    "comercio_relacionado": perfil['nombre_comercio']
                                }).execute()
                                st.success("¡Producto en línea!"); st.rerun()
            
            st.divider()
            for mp in mis_prods:
                col_a, col_b = st.columns([4, 1])
                col_a.write(f"🔹 {mp['nombre_producto']} - ${mp['precio']}")
                if col_b.button("🗑️", key=f"del_{mp['id']}"):
                    supabase.table("productos").delete().eq("id", mp['id']).execute()
                    st.rerun()

        with tab2:
            nuevo_pago = st.text_area("Datos para que te paguen (Pago Móvil, Zelle, etc.)", value=perfil.get('datos_pago', ''))
            if st.button("ACTUALIZAR DATOS"):
                supabase.table("perfiles_comercio").update({"datos_pago": nuevo_pago}).eq("id", perfil['id']).execute()
                st.success("Actualizado")
            if st.button("CERRAR SESIÓN"):
                st.session_state.logged_in = False
                st.rerun()