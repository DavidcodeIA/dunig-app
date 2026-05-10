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
# 5. CONTROLADOR DE VISTAS (UNIFICADO)
# ==========================================

# HEADER SUPERIOR CON ICONOS (Visible en todas las vistas)
col_t, col_btn1, col_btn2 = st.columns([6, 1, 1])
with col_t:
    st.markdown("<h3 style='color:#D4AF37; margin:0; cursor:pointer;' onclick='window.location.reload()'>D'UNIG LUXURY MALL</h3>", unsafe_allow_html=True)
with col_btn1:
    if st.button("➕", help="Registrar mi negocio"):
        st.query_params.clear() # Limpiamos para salir de admin si estaba ahí
        ir_a('registro')
with col_btn2:
    if st.button("⚙️", help="Panel de Control"):
        st.query_params["admin"] = "true"
        st.rerun()

es_admin_url = st.query_params.get("admin") == "true"

# --- A. VISTA: ADMIN (PANEL DE CONTROL) ---
if es_admin_url:
    st.markdown("<h2 style='text-align:center;'>⚙️ MI PANEL DE CONTROL</h2>", unsafe_allow_html=True)
    
    if not st.session_state.get('logged_in', False):
        with st.container(border=True):
            e_log = st.text_input("Email de socio").lower().strip()
            c_log = st.text_input("Código de acceso", type="password")
            if st.button("INGRESAR AL PANEL"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", e_log).execute()
                if res.data and str(res.data[0]['codigo_acceso']) == c_log:
                    st.session_state.logged_in = True
                    st.session_state.user_email = e_log
                    st.rerun()
                else: st.error("Credenciales incorrectas")
        if st.button("⬅️ Volver al Mall"):
            st.query_params.clear()
            ir_a('mall')
    else:
        perf = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        tab1, tab2, tab3 = st.tabs(["📤 SUBIR PRODUCTO", "📦 MI INVENTARIO", "🖼️ MI PERFIL"])
        
        with tab1:
            with st.form("subir_p", clear_on_submit=True):
                n = st.text_input("Nombre del Producto")
                p = st.number_input("Precio ($)", min_value=0.0)
                v = st.file_uploader("Video (MP4)", type=['mp4'])
                if st.form_submit_button("💎 PUBLICAR"):
                    if n and v:
                        url = subir_archivo(v, "videos")
                        supabase.table("productos").insert({"nombre_producto": n, "precio": p, "video_url": url, "comercio_relacionado": perf['nombre_comercio']}).execute()
                        st.success("¡Producto en vitrina!")
                        time.sleep(1); st.rerun()

        with tab2:
            st.subheader("Gestión de Productos")
            prods = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute().data
            for p in prods:
                with st.expander(f"📦 {p['nombre_producto']} - ${p['precio']}"):
                    st.video(p['video_url'])
                    if st.button(f"🗑️ Eliminar {p['nombre_producto']}", key=f"del_{p['id']}"):
                        supabase.table("productos").delete().eq("id", p['id']).execute()
                        st.warning("Eliminado"); time.sleep(1); st.rerun()

        with tab3:
            st.subheader("Editar Perfil")
            if perf.get('portada_url'): st.image(perf['portada_url'], width=150)
            nueva_foto = st.file_uploader("Actualizar Foto", type=['jpg', 'png'])
            nueva_cat = st.selectbox("Categoría", CATEGORIAS, index=CATEGORIAS.index(perf['categoria']) if perf['categoria'] in CATEGORIAS else 0)
            if st.button("💾 GUARDAR CAMBIOS"):
                updates = {"categoria": nueva_cat}
                if nueva_foto: updates["portada_url"] = subir_archivo(nueva_foto, "portadas")
                supabase.table("perfiles_comercio").update(updates).eq("id", perf['id']).execute()
                st.success("Actualizado"); time.sleep(1); st.rerun()
        
        if st.button("SALIR DEL PANEL"):
            st.session_state.logged_in = False
            st.query_params.clear()
            ir_a('mall')

# --- B. VISTA: REGISTRO ---
elif st.session_state.view == 'registro':
    st.markdown("<h1 style='text-align:center;'>💎 REGISTRO DE SOCIO</h1>", unsafe_allow_html=True)
    with st.form("registro_socio"):
        cat_reg = st.selectbox("Categoría", CATEGORIAS)
        rn = st.text_input("Nombre Negocio")
        re = st.text_input("Email").lower().strip()
        rw = st.text_input("WhatsApp (Ej: 58412...)")
        rf = st.file_uploader("Logo/Portada", type=['jpg','png'])
        ref_pago = st.text_input("Referencia Pago")
        if st.form_submit_button("🚀 ENVIAR SOLICITUD"):
            portada = subir_archivo(rf, "portadas")
            cod = str(random.randint(100000, 999999))
            supabase.table("perfiles_comercio").insert({
                "nombre_comercio": rn, "email_propietario": re, "whatsapp": rw,
                "categoria": cat_reg, "portada_url": portada, "codigo_acceso": cod, "activo": False, "referencia_pago": ref_pago
            }).execute()
            st.success(f"¡Solicitud Enviada! TU CÓDIGO: {cod}")
    if st.button("VOLVER AL MALL"): ir_a('mall')

# --- C. VISTA: MALL ---
elif st.session_state.view == 'mall':
    col1, col2 = st.columns([2, 1])
    with col1: busq = st.text_input("🔍 Buscar comercio...", "").lower()
    with col2: cat_f = st.selectbox("Rubro", ["Todas"] + CATEGORIAS)

    query = supabase.table("perfiles_comercio").select("*").eq("activo", True)
    if cat_f != "Todas": query = query.eq("categoria", cat_f)
    tiendas = [t for t in query.execute().data if busq in t['nombre_comercio'].lower()]

    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i+j < len(tiendas):
                t = tiendas[i+j]
                with cols[j]:
                    st.markdown(f'<img src="{t.get("portada_url")}" class="img-redonda">', unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align:center; font-weight:bold;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                    if st.button("ENTRAR", key=f"mall_{t['id']}"):
                        st.session_state.tienda_actual = t
                        ir_a('tienda')

# --- D. VISTA: TIENDA (CON CARRITO NARANJA Y GESTIÓN EN VIVO) ---
elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    
    # Header de la Tienda con Acceso Directo al Carrito
    c_back, c_title, c_cart = st.columns([1, 4, 1])
    with c_back:
        if st.button("⬅️"): ir_a('mall')
    with c_title:
        st.markdown(f"<h2 style='text-align:center; margin:0;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    with c_cart:
        # Acceso directo superior (Checkout)
        cant_items = sum(item['cantidad'] for item in st.session_state.cart)
        if st.button(f"🛒 {cant_items if cant_items > 0 else ''}"):
            ventana_carrito()

    st.divider()
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    if not prods:
        st.info("Esta tienda aún no tiene productos en vitrina.")
    
    for p in prods:
        with st.container():
            # Contenedor del Video con "Carrito Naranja" superpuesto
            # Simulamos el overlay con columnas o contenedores de Streamlit
            st.video(p['video_url'])
            
            col_info, col_accion = st.columns([3, 1])
            
            with col_info:
                st.markdown(f"**{p['nombre_producto']}**")
                st.markdown(f"<span style='color:#D4AF37; font-size:1.2em;'>${p['precio']}</span>", unsafe_allow_html=True)
                
                # Indicador de "Compras Activas" (Número rojo estilo vivo)
                compras_simuladas = random.randint(1, 15)
                st.markdown(f"🔥 <span style='color:#ff4b4b; font-weight:bold;'>{compras_simuladas} personas comprando</span>", unsafe_allow_html=True)

            with col_accion:
                # El ÍCONO DISTINTIVO (Carrito Naranja)
                if st.button("🟠", key=f"naranja_{p['id']}", help="Añadir rápido"):
                    # Lógica de añadir o incrementar
                    item_existente = next((item for item in st.session_state.cart if item['id'] == p['id']), None)
                    if item_existente:
                        item_existente['cantidad'] += 1
                    else:
                        st.session_state.cart.append({
                            "id": p['id'], 
                            "nombre": p['nombre_producto'], 
                            "precio": p['precio'], 
                            "cantidad": 1
                        })
                    st.toast(f"¡{p['nombre_producto']} al carrito!")
                    st.rerun()

    # Botón Flotante Inferior (Opcional, para Checkout rápido)
    if st.session_state.cart:
        st.markdown("---")
        if st.button("🛍️ PROCEDER AL PAGO (CHECKOUT)", use_container_width=True):
            ventana_carrito()