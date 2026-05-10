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
    "GRATUITO": {"limite": 3, "precio": "0", "color": "#C0C0C0", "beneficios": ["3 Productos", "Video Reels", "Soporte Email"]},
    "BRONCE": {"limite": 10, "precio": "5", "color": "#CD7F32", "beneficios": ["10 Productos", "Video Reels", "Soporte WhatsApp"]},
    "PLATA": {"limite": 25, "precio": "15", "color": "#E5E4E2", "beneficios": ["25 Productos", "Video Reels", "Estadísticas"]},
    "ORO": {"limite": 100, "precio": "30", "color": "#D4AF37", "beneficios": ["100 Productos", "Video Reels", "Prioridad VIP"]}
}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'cart' not in st.session_state: st.session_state.cart = []

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

def subir_archivo(file, folder):
    try:
        ext = file.name.split(".")[-1]
        filename = f"{folder}/{uuid.uuid4()}.{ext}"
        supabase.storage.from_("luxury_assets").upload(filename, file.read())
        return supabase.storage.from_("luxury_assets").get_public_url(filename)
    except Exception as e:
        st.error(f"Error: {e}"); return None

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: #000; color: #fff; }
    .img-redonda {
        width: 180px; height: 180px; border-radius: 50%;
        object-fit: cover; border: 2px solid #D4AF37;
        margin: 0 auto 15px auto; display: block;
        box-shadow: 0px 8px 20px rgba(212, 175, 55, 0.3);
    }
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 8px !important;
        font-weight: 800 !important; height: 45px !important; width: 100% !important;
        border: none !important;
    }
    .btn-carrito-fix > button {
        background: rgba(255,255,255,0.1) !important;
        color: #D4AF37 !important;
        border: 1px solid #D4AF37 !important;
        margin-bottom: 5px !important;
        height: 35px !important;
    }
    .product-info { text-align: center; margin: 10px 0; font-size: 1.3rem; font-weight: bold; }
    .price-tag { color: #39FF14; margin-left: 10px; }
    .plan-card {
        border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 12px; 
        padding: 15px; text-align: center; background: #0a0a0a; min-height: 350px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGO DEL CARRITO
# ==========================================
@st.dialog("🛒 RESUMEN DE COMPRA")
def ventana_carrito():
    if not st.session_state.cart:
        st.write("El carrito está vacío.")
        return
    total = sum(item['precio'] * item['cantidad'] for item in st.session_state.cart)
    for i, item in enumerate(st.session_state.cart):
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"**{item['nombre']}**")
        c2.write(f"x{item['cantidad']}")
        c3.write(f"${item['precio']*item['cantidad']:,.2f}")
        if st.button("🗑️", key=f"del_{i}"):
            st.session_state.cart.pop(i); st.rerun()
    st.divider()
    st.subheader(f"Total: ${total:,.2f}")
    t = st.session_state.tienda_actual
    ref = st.text_input("Referencia de Pago (Transferencia/Móvil)")
    if st.button("💎 FINALIZAR Y ENVIAR WHATSAPP") and ref:
        prods_txt = "\n".join([f"- {x['nombre']} (x{x['cantidad']})" for x in st.session_state.cart])
        msj = f"✨ *NUEVO PEDIDO*\n\n🏪 {t['nombre_comercio']}\n📦 *Productos:*\n{prods_txt}\n\n💰 *Total:* ${total:,.2f}\n🎫 *Ref:* {ref}"
        st.session_state.cart = []
        st.link_button("ABRIR WHATSAPP", f"https://wa.me/{str(t['whatsapp']).strip()}?text={urllib.parse.quote(msj)}")

# ==========================================
# 4. VISTAS
# ==========================================
es_admin = st.query_params.get("admin") == "true"
es_reg = st.query_params.get("reg") == "true"

if es_reg:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>BENEFICIOS SOCIOS</h1>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, (nombre, info) in enumerate(PLANES.items()):
        with cols[i]:
            st.markdown(f'<div class="plan-card"><h3 style="color:{info["color"]}">{nombre}</h3><h2>${info["precio"]}</h2><hr>' + "".join([f"<p style='font-size:0.8rem;'>✅ {b}</p>" for b in info["beneficios"]]) + '</div>', unsafe_allow_html=True)
    # Formulario simplificado... (se mantiene igual al anterior)

elif es_admin:
    # Panel de control (se mantiene igual al anterior con el blindaje de KeyError)
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL ADMIN</h1>", unsafe_allow_html=True)
    # ... (Lógica de login y gestión de productos)

elif st.session_state.view == 'mall':
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
    busq = st.text_input("🔍 Buscar tiendas...", "").lower()
    tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
    tiendas = [t for t in tiendas if busq in t['nombre_comercio'].lower()]
    for i in range(0, len(tiendas), 2):
        cols = st.columns(2)
        for j in range(2):
            if i+j < len(tiendas):
                t = tiendas[i+j]
                with cols[j]:
                    st.markdown(f'<img src="{t["portada_url"]}" class="img-redonda">', unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align:center;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                    if st.button("ENTRAR", key=t['id'], use_container_width=True):
                        st.session_state.tienda_actual = t; ir_a('tienda')

elif st.session_state.view == 'tienda':
    t = st.session_state.tienda_actual
    if st.button("⬅️ VOLVER AL MALL"): 
        st.session_state.cart = []; ir_a('mall')
    
    st.markdown(f"<h2 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h2>", unsafe_allow_html=True)
    
    prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
    
    for p in prods:
        st.video(p['video_url'], autoplay=True, loop=True, muted=True)
        st.markdown(f'<div class="product-info">{p["nombre_producto"].upper()} <span class="price-tag">${p["precio"]}</span></div>', unsafe_allow_html=True)
        
        # --- NUEVA INTERFAZ DE COMPRA ---
        cant_items = sum(item['cantidad'] for item in st.session_state.cart)
        
        # Botón de Carrito (solo aparece si hay algo)
        if cant_items > 0:
            st.markdown('<div class="btn-carrito-fix">', unsafe_allow_html=True)
            if st.button(f"🛒 VER CARRITO ({cant_items} items)", key=f"view_cart_{p['id']}"):
                ventana_carrito()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Botón Añadir (ahora añade de 1 en 1 directamente)
        if st.button(f"➕ AÑADIR AL CARRITO", key=f"add_{p['id']}", use_container_width=True):
            # Buscar si ya existe para sumar cantidad
            found = False
            for item in st.session_state.cart:
                if item['id'] == p['id']:
                    item['cantidad'] += 1
                    found = True; break
            if not found:
                st.session_state.cart.append({"id":p['id'], "nombre":p['nombre_producto'], "precio":p['precio'], "cantidad":1})
            st.toast(f"Añadido: {p['nombre_producto']}")
            st.rerun()
            
        st.divider()