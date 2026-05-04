import streamlit as st
from supabase import create_client, Client
import random

# Esto debe ser lo primero que vea Streamlit
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide")

# --- CONEXIÓN ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- ESTADOS ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None
if 'carrito' not in st.session_state: st.session_state.carrito = {}

def navegar(destino, com=None):
    st.session_state.pagina = destino
    if com: st.session_state.comercio_sel = com
    st.rerun()

# --- ESTILOS INCLUYENDO BOTÓN FLOTANTE ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .floating-cart {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #D4AF37;
        color: black;
        padding: 20px;
        border-radius: 50px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        z-index: 1000;
        cursor: pointer;
        font-weight: bold;
    }
    .video-card { border: 1px solid #333; border-radius: 15px; padding: 10px; margin-bottom: 20px; background: #111; }
    .price { color: #D4AF37; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# LÓGICA DE PÁGINAS
# ==========================================

# --- INICIO --- (Código igual al anterior...)
if st.session_state.pagina == "inicio":
    st.markdown("<h1 style='text-align:center;'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: st.button("🛒 ENTRAR AL CENTRO", use_container_width=True, on_click=navegar, args=("centro_comercial",))
    with c2: st.button("🏢 PROPIETARIOS", use_container_width=True, on_click=navegar, args=("login_comercio",))

# --- CENTRO COMERCIAL ---
elif st.session_state.pagina == "centro_comercial":
    st.title("🏢 CENTRO COMERCIAL")
    tiendas = supabase.table("perfiles_comercio").select("*").execute()
    cols = st.columns(3)
    for i, t in enumerate(tiendas.data):
        with cols[i % 3]:
            st.image(t.get('logo_url', ''), width=100)
            st.subheader(t['nombre_comercio'])
            st.button("Entrar", key=f"t_{i}", on_click=navegar, args=("vitrina_personal", t['nombre_comercio']))
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- VITRINA PERSONAL (CON BOTÓN FLOTANTE) ---
elif st.session_state.pagina == "vitrina_personal":
    tienda_nom = st.session_state.comercio_sel
    st.title(f"🏪 {tienda_nom}")
    
    # Obtener productos
    prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda_nom).execute()
    
    for p in prods.data:
        with st.container():
            st.markdown("<div class='video-card'>", unsafe_allow_html=True)
            st.video(p['video_url'])
            st.subheader(p['nombre_producto'])
            st.markdown(f"<p class='price'>{p['precio']}$</p>", unsafe_allow_html=True)
            
            pid = str(p['id'])
            cant = st.session_state.carrito.get(pid, 0)
            c1, c2, c3 = st.columns([1,1,4])
            if c1.button("➖", key=f"m_{pid}"):
                st.session_state.carrito[pid] = max(0, cant - 1)
                st.rerun()
            c2.write(f"### {cant}")
            if c3.button("➕", key=f"p_{pid}"):
                st.session_state.carrito[pid] = cant + 1
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # LÓGICA DEL BOTÓN FLOTANTE
    total_items = sum(st.session_state.carrito.values())
    if total_items > 0:
        st.markdown(f"""
            <div class="floating-cart" onclick="window.location.reload();">
                🛒 {total_items} Productos en Carrito
            </div>
            """, unsafe_allow_html=True)
        if st.button("📦 IR A PAGAR AHORA", use_container_width=True):
            navegar("pago")

# --- PÁGINA DE PAGO (CON GPS Y REFERENCIA) ---
elif st.session_state.pagina == "pago":
    tienda_nom = st.session_state.comercio_sel
    perfil = supabase.table("perfiles_comercio").select("*").eq("nombre_comercio", tienda_nom).single().execute()
    
    st.title("🏁 TICKET DE PAGO")
    
    # 1. LOCALIZACIÓN GPS
    st.subheader("📍 Tu Ubicación para Entrega")
    loc = get_geolocation()
    mapa_url = ""
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        mapa_url = f"https://www.google.com/maps?q={lat},{lon}"
        st.success("✅ Ubicación detectada correctamente")
    else:
        st.warning("Por favor, permite el acceso al GPS para el delivery.")

    # 2. RESUMEN DE PRODUCTOS
    st.subheader("📝 Resumen del Pedido")
    total_final = 0
    resumen_texto = ""
    prods_res = supabase.table("productos").select("*").eq("comercio_propietario", tienda_nom).execute()
    
    for pr in prods_res.data:
        id_p = str(pr['id'])
        cant = st.session_state.carrito.get(id_p, 0)
        if cant > 0:
            sub = pr['precio'] * cant
            total_final += sub
            st.write(f"✅ {pr['nombre_producto']} x{cant} = {sub}$")
            resumen_texto += f"- {pr['nombre_producto']} (x{cant}): {sub}$%0A"

    st.markdown(f"### TOTAL A PAGAR: {total_final}$")
    
    # 3. DATOS DE PAGO Y REFERENCIA
    st.markdown("---")
    st.subheader("💰 Instrucciones de Pago")
    st.info(perfil.data.get('datos_pago', 'Consultar al vendedor'))
    
    ref_pago = st.text_input("🔢 Número de Referencia o Captura")
    
    # 4. BOTÓN FINAL WHATSAPP
    if st.button("🚀 CONFIRMAR Y ENVIAR AL VENDEDOR"):
        if ref_pago:
            # Construir mensaje final
            msg = f"*ORDEN DE COMPRA - D'UNIG*%0A"
            msg += f"Tienda: {tienda_nom}%0A"
            msg += f"---%0A{resumen_texto}"
            msg += f"---%0A*TOTAL: {total_final}$*%0A"
            msg += f"Ref: {ref_pago}%0A"
            if mapa_url: msg += f"📍 Ubicación: {mapa_url}"
            
            ws = perfil.data.get('whatsapp', '')
            url_wa = f"https://wa.me/{ws}?text={msg}"
            st.markdown(f'<a href="{url_wa}" target="_blank" style="background-color:#25D366;color:white;padding:15px;border-radius:10px;text-decoration:none;display:block;text-align:center;">ABRIR WHATSAPP</a>', unsafe_allow_html=True)
        else:
            st.error("Por favor, ingresa el número de referencia del pago.")

    st.button("🔙 CANCELAR", on_click=navegar, args=("vitrina_personal", tienda_nom))

# --- PANEL DE CARGA --- (Mantén tu código anterior aquí igual)
