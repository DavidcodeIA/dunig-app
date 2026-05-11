import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random
import uuid
import time

# ==========================================
# 1. CONFIGURACIÓN Y CONSTANTES
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

# Lista Maestra de Categorías
CATEGORIAS = [
    "🍎 Fruterías", "🥩 Carnicerías", "🥖 Panaderías", "🍴 Restaurantes", "🏨 Hoteles", 
    "🚕 Servicios de transporte", "🛒 Supermercados", "🛠️ Repuestos para vehículos", 
    "🏠 Inmobiliarias", "💊 Farmacias", "👕 Ropa y Calzado", "🪅 Piñaterías", 
    "🎉 Agencia de festejos", "💈 Barberías", "✨ Otros"
]

PLANES = {
    "GRATUITO": {"limite": 3, "precio": "0", "color": "#C0C0C0", "beneficios": ["3 Productos", "Video Reels", "Panel Básico"]},
    "BRONCE": {"limite": 10, "precio": "5", "color": "#CD7F32", "beneficios": ["10 Productos", "Video Reels", "Panel Pro"]},
    "PLATA": {"limite": 25, "precio": "15", "color": "#E5E4E2", "beneficios": ["25 Productos", "Video Reels", "Estadísticas"]},
    "ORO": {"limite": 100, "precio": "30", "color": "#D4AF37", "beneficios": ["100 Productos", "Video Reels", "Prioridad VIP"]}
}

# ==========================================
# 2. CONEXIÓN Y FUNCIONES DE APOYO
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

def subir_archivo(file, folder):
    try:
        ext = file.name.split(".")[-1]
        filename = f"{folder}/{uuid.uuid4()}.{ext}"
        supabase.storage.from_("fotos_productos").upload(filename, file.read())
        return supabase.storage.from_("fotos_productos").get_public_url(filename)
    except Exception as e:
        st.error(f"Error al subir: {e}"); return None

# Inicialización de Estados
if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = []
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

# ==========================================
# 3. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000; color: #fff; }
    .img-redonda {
        width: 160px; height: 160px; border-radius: 50%;
        object-fit: cover; border: 2px solid #D4AF37;
        margin: 0 auto 10px auto; display: block;
        box-shadow: 0px 5px 15px rgba(212, 175, 55, 0.3);
    }
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #8A6E2F) !important;
        color: #000 !important; border-radius: 8px !important;
        font-weight: bold !important; width: 100% !important;
    }
    .plan-card {
        border: 1px solid rgba(212, 175, 55, 0.2); border-radius: 10px; 
        padding: 15px; text-align: center; background: #0a0a0a; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. DIÁLOGO DEL CARRITO
# ==========================================
@st.dialog("🛒 TU PEDIDO LUXURY")
def ventana_carrito():
    if not st.session_state.cart:
        st.write("El carrito está vacío.")
        return
    total = sum(item['precio'] * item['cantidad'] for item in st.session_state.cart)
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(item['nombre'])
        c2.write(f"x{item['cantidad']}")
        c3.write(f"${item['precio']*item['cantidad']}")
    st.divider()
    t = st.session_state.tienda_actual
    ref = st.text_input("Referencia de Pago")
    if st.button("💎 CONFIRMAR Y ENVIAR"):
        msj = f"NUEVO PEDIDO: {t['nombre_comercio']}\nTotal: ${total}\nRef: {ref}"
        st.link_button("WHATSAPP", f"https://wa.me/{t['whatsapp']}?text={urllib.parse.quote(msj)}")

# ==========================================
# 5. BARRA DE NAVEGACIÓN LUXURY (ICONOS EN FILA)
# ==========================================
cant_items = sum(item['cantidad'] for item in st.session_state.cart)

# Layout de la barra superior
c_tit, c_reg, c_adm, c_car, c_pay = st.columns([3, 1, 1, 1, 1])

with c_tit:
    st.markdown("<h3 style='color:#D4AF37; margin:0;'>D'UNIG</h3>", unsafe_allow_html=True)

with c_reg:
    if st.button("➕", help="Registrar mi negocio"):
        st.query_params.clear()
        ir_a('registro')

with c_adm:
    if st.button("⚙️", help="Panel de Control"):
        st.query_params["admin"] = "true"
        st.rerun()

with c_car:
    # Icono Carrito Naranja que suma 🟧
    if st.button(f"🛒{cant_items if cant_items > 0 else ''}", key="nav_cart"):
        ventana_carrito()

with c_pay:
    # Icono de Pago/Checkout 🔴
    if st.button("💳", key="nav_pay"):
        if st.session_state.cart: ventana_carrito()
        else: st.toast("Carrito vacío")

st.divider()

# ==========================================
# 6. LÓGICA DE VISTAS INTEGRADA
# ==========================================
es_admin_url = st.query_params.get("admin") == "true"

# --- A. VISTA: ADMIN ---
if es_admin_url:
    st.markdown("<h2 style='text-align:center;'>⚙️ PANEL DE CONTROL</h2>", unsafe_allow_html=True)
    if not st.session_state.get('logged_in', False):
        with st.container(border=True):
            e_log = st.text_input("Email").lower().strip()
            c_log = st.text_input("Código", type="password")
            if st.button("INGRESAR"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", e_log).execute()
                if res.data and str(res.data[0]['codigo_acceso']) == c_log:
                    st.session_state.logged_in = True
                    st.session_state.user_email = e_log
                    st.rerun()
                else: st.error("Error de acceso")
    else:
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        t1, t2, t3 = st.tabs(["📤 SUBIR", "📦 INVENTARIO", "🖼️ PERFIL"])
        with t1:
            with st.form("p_sub"):
                n = st.text_input("Nombre")
                p = st.number_input("Precio", min_value=0.0)
                v = st.file_uploader("Video", type=['mp4'])
                if st.form_submit_button("PUBLICAR"):
                    url = subir_archivo(v, "videos")
                    supabase.table("productos").insert({"nombre_producto":n, "precio":p, "video_url":url, "comercio_relacionado":perf['nombre_comercio']}).execute()
                    st.success("¡Listo!"); time.sleep(1); st.rerun()
        with t2:
            prods = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            for pr in prods:
                with st.expander(f"{pr['nombre_producto']}"):
                    if st.button(f"Eliminar {pr['id']}", key=f"del_{pr['id']}"):
                        supabase.table("productos").delete().eq("id", pr['id']).execute()
                        st.rerun()
        with t3:
            if st.button("CERRAR SESIÓN"):
                st.session_state.logged_in = False
                st.query_params.clear()
                ir_a('mall')

# --- B. VISTA: REGISTRO ---
elif st.session_state.view == 'registro':
    st.markdown("<h2 style='text-align:center;'>💎 REGISTRO</h2>", unsafe_allow_html=True)
    with st.form("reg"):
        cat = st.selectbox("Categoría", CATEGORIAS)
        nom = st.text_input("Negocio")
        em = st.text_input("Email")
        tel = st.text_input("WhatsApp")
        img = st.file_uploader("Portada", type=['jpg', 'png'])
        pago = st.text_input("Referencia Pago")
        if st.form_submit_button("ENVIAR"):
            url_img = subir_archivo(img, "portadas")
            cod = str(random.randint(100000, 999999))
            supabase.table("perfiles_comercio").insert({
                "nombre_comercio": nom, "email_propietario": em, "whatsapp": tel,
                "categoria": cat, "portada_url": url_img, "codigo_acceso": cod, "activo": False, "referencia_pago": pago
            }).execute()
            st.success(f"Código: {cod}")
    if st.button("VOLVER"): ir_a('mall')

# --- C. VISTA: MALL ---
elif st.session_state.view == 'mall':
    c1, c2 = st.columns([2, 1])
    with c1: b = st.text_input("🔍 Buscar...").lower()
    with c2: cf = st.selectbox("Filtro", ["Todas"] + CATEGORIAS)
    
    q = supabase.table("perfiles_comercio").select("*").eq("activo", True)
    if cf != "Todas": q = q.eq("categoria", cf)
    tiendas = [t for t in q.execute().data if b in t['nombre_comercio'].lower()]
    
    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i+j < len(tiendas):
                ti = tiendas[i+j]
                with cols[j]:
                    st.image(ti.get("portada_url"), use_container_width=True)
                    if st.button(f"ENTRAR {ti['nombre_comercio']}", key=f"btn_{ti['id']}"):
                        st.session_state.tienda_actual = ti
                        ir_a('tienda')

# --- BLOQUE DE VISTA: FEED DE VIDEOS UNIDOS (CONTINUOUS SCROLL) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    
    # CSS para unir los videos y el overlay
    st.markdown("""
        <style>
            /* Elimina el espacio que Streamlit pone entre bloques por defecto */
            [data-testid="stVerticalBlock"] > div {
                gap: 0px !important;
                padding-bottom: 0px !important;
                margin-bottom: 0px !important;
            }

            .video-stack {
                position: relative;
                width: 100%;
                /* Ajuste de altura para que casi llene la pantalla del móvil */
                height: 85vh; 
                background-color: black;
                overflow: hidden;
                /* Sin margen inferior para que se peguen */
                margin: 0px !important;
                padding: 0px !important;
                border-bottom: 1px solid #222; /* Una línea casi invisible solo para distinguir */
            }
            
            video {
                width: 100% !important;
                height: 100% !important;
                object-fit: cover; /* Importante para que el video llene el área sin dejar bandas negras */
            }

            .side-controls {
                position: absolute;
                right: 15px;
                bottom: 100px;
                z-index: 100;
            }

            .bottom-info {
                position: absolute;
                left: 15px;
                bottom: 25px;
                color: white;
                text-shadow: 2px 2px 5px rgba(0,0,0,0.9);
                z-index: 90;
            }

            /* Botones flotantes minimalistas */
            .stButton button {
                background: rgba(0, 0, 0, 0.4) !important;
                backdrop-filter: blur(8px);
                border: 1px solid rgba(212, 175, 55, 0.6) !important;
                border-radius: 50% !important;
                width: 50px !important;
                height: 50px !important;
                margin-bottom: 10px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # Botón volver flotante (puedes ponerlo también como overlay si prefieres)
    if st.button("⬅️", key="back_nav"): ir_a('mall')

    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        # Contenedor Stack sin separadores intermedios
        st.markdown(f'<div class="video-stack">', unsafe_allow_html=True)
        
        # 1. El Video de fondo (con autoplay y loop para el efecto reel)
        st.video(p['video_url'])
        
        # 2. La Info pegada abajo
        st.markdown(f"""
            <div class="bottom-info">
                <b style='font-size:1.2em; color:#D4AF37;'>@{t['nombre_comercio']}</b><br>
                <span style='font-size:1em;'>{p['nombre_producto']}</span><br>
                <span style='font-size:1.4em; font-weight:bold;'>${p['precio']}</span>
            </div>
        """, unsafe_allow_html=True)

        # 3. Los Botones flotantes (Stack lateral)
        with st.container():
            # Usamos columnas para posicionar los botones a la derecha del video
            c_v, c_btns = st.columns([8.2, 1.8])
            with c_btns:
                # El truco del margen negativo para subirlos sobre el video
                st.markdown('<div style="margin-top: -320px;">', unsafe_allow_html=True)
                if st.button("➕", key=f"f_reg_{p['id']}"): ir_a('registro')
                if st.button("⚙️", key=f"f_adm_{p['id']}"): 
                    st.query_params["admin"] = "true"
                    st.rerun()
                if st.button("🟠", key=f"f_car_{p['id']}"):
                    st.session_state.cart.append({"id":p['id'], "nombre":p['nombre_producto'], "precio":p['precio'], "cantidad":1})
                    st.toast("Añadido")
                if st.button("💳", key=f"f_pay_{p['id']}"):
                    if not any(item['id'] == p['id'] for item in st.session_state.cart):
                        st.session_state.cart.append({"id":p['id'], "nombre":p['nombre_producto'], "precio":p['precio'], "cantidad":1})
                    ventana_carrito()
                st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
        # NOTA: Aquí ya NO hay dividers ni espacios. El bucle pega el siguiente div al anterior.