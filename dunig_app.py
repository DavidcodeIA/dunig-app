import streamlit as st
from supabase import create_client, Client
import random
import re

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", page_icon="⚜️")

# --- 2. CONEXIÓN A SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- 3. ESTADOS DE SESIÓN Y NAVEGACIÓN ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None
if 'carrito' not in st.session_state: st.session_state.carrito = {}

def navegar(destino, com=None):
    st.session_state.pagina = destino
    if com: 
        st.session_state.comercio_sel = com
    st.rerun()

# --- 4. DISEÑO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .card-tienda { border: 1px solid #D4AF37; padding: 20px; border-radius: 20px; background: #1A1C23; text-align: center; margin-bottom: 10px; }
    .video-container { border-bottom: 2px solid #333; padding-bottom: 30px; margin-bottom: 30px; background: #111; border-radius: 15px; padding: 10px; }
    .price-tag { color: #D4AF37; font-size: 28px; font-weight: bold; }
    .btn-carrito { background-color: #D4AF37; color: black; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# LÓGICA DE PÁGINAS
# ==========================================

# --- PÁGINA: INICIO ---
if st.session_state.pagina == "inicio":
    st.markdown("<h1 style='text-align:center;'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>La nueva forma de comprar por video</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛒 ENTRAR AL CENTRO COMERCIAL", use_container_width=True):
            navegar("centro_comercial")
    with c2:
        if st.button("🏢 PANEL DE PROPIETARIOS", use_container_width=True):
            navegar("login_comercio")

# --- PÁGINA: LOGIN COMERCIO ---
elif st.session_state.pagina == "login_comercio":
    st.subheader("🔑 Acceso Propietario")
    nom = st.text_input("Nombre de tu Negocio (Sin espacios preferiblemente)")
    if st.button("INGRESAR AL PANEL"):
        if nom:
            st.session_state.comercio_sesion = nom
            navegar("panel_carga")
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",))

# --- PÁGINA: PANEL DE CARGA ---
elif st.session_state.pagina == "panel_carga":
    nombre_c = st.session_state.comercio_sesion
    st.title(f"⚙️ Gestión: {nombre_c}")
    
    # SECCIÓN PERFIL
    with st.expander("🖼️ CONFIGURAR PERFIL (Logo, WhatsApp, Pago)"):
        logo = st.file_uploader("Logo del Negocio", type=['jpg','png'])
        ws = st.text_input("WhatsApp (Ej: 584121234567)")
        pago = st.text_area("Instrucciones de Pago (Bancos, Pago Móvil, etc.)")
        
        if st.button("Guardar Datos del Perfil"):
            try:
                url_l = None
                if logo:
                    nom_logo = re.sub(r'[^a-zA-Z0-9]', '_', logo.name)
                    path_l = f"logos/{nombre_c}_{nom_logo}"
                    supabase.storage.from_("fotos_productos").upload(path_l, logo.getvalue())
                    url_l = supabase.storage.from_("fotos_productos").get_public_url(path_l)
                
                data = {"nombre_comercio": nombre_c, "whatsapp": ws, "datos_pago": pago}
                if url_l: data["logo_url"] = url_l
                
                supabase.table("perfiles_comercio").upsert(data, on_conflict="nombre_comercio").execute()
                st.success("✅ Perfil actualizado")
            except Exception as e:
                st.error(f"Error al guardar perfil: {e}")

    # SECCIÓN CARGA DE VIDEO
    with st.form("form_video", clear_on_submit=True):
        st.subheader("🎬 Publicar Video-Producto")
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0)
        p_vid = st.file_uploader("Video (MP4 recomendado)", type=['mp4', 'mov'])
        
        if st.form_submit_button("🚀 PUBLICAR AHORA"):
            if p_nom and p_vid:
                try:
                    with st.status("Subiendo video..."):
                        # Limpieza de nombre para evitar InvalidKey Error
                        nom_v_limpio = re.sub(r'[^a-zA-Z0-9]', '_', p_vid.name)
                        path_v = f"productos/{random.randint(100,999)}_{nom_v_limpio}"
                        
                        supabase.storage.from_("fotos_productos").upload(
                            path=path_v, 
                            file=p_vid.getvalue(),
                            file_options={"content-type": "video/mp4"}
                        )
                        url_v = supabase.storage.from_("fotos_productos").get_public_url(path_v)
                        
                        supabase.table("productos").insert({
                            "nombre_producto": p_nom, 
                            "precio": p_pre, 
                            "video_url": url_v, 
                            "comercio_propietario": nombre_c
                        }).execute()
                    st.success("¡Video publicado en tu vitrina!")
                except Exception as e:
                    st.error(f"Error de carga: {e}")
            else:
                st.warning("Completa el nombre y el video.")

    st.button("🏠 CERRAR SESIÓN", on_click=navegar, args=("inicio",))

# --- PÁGINA: CENTRO COMERCIAL ---
elif st.session_state.pagina == "centro_comercial":
    st.title("🏢 CENTRO COMERCIAL D'UNIG")
    try:
        tiendas = supabase.table("perfiles_comercio").select("*").execute()
        if tiendas.data:
            cols = st.columns(3)
            for i, t in enumerate(tiendas.data):
                with cols[i % 3]:
                    st.markdown("<div class='card-tienda'>", unsafe_allow_html=True)
                    if t.get('logo_url'): 
                        st.image(t['logo_url'], width=120)
                    st.subheader(t['nombre_comercio'])
                    if st.button(f"Visitar {t['nombre_comercio']}", key=f"t_{i}"):
                        navegar("vitrina_personal", t['nombre_comercio'])
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Aún no hay tiendas registradas.")
    except Exception as e:
        st.error(f"Error: {e}")
    st.button("🔙 VOLVER AL INICIO", on_click=navegar, args=("inicio",))

# --- PÁGINA: VITRINA (MODO TIKTOK) ---
elif st.session_state.pagina == "vitrina_personal":
    tienda_nom = st.session_state.comercio_sel
    st.title(f"🏪 Tienda: {tienda_nom}")
    
    prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda_nom).execute()
    
    if prods.data:
        for p in prods.data:
            with st.container():
                st.markdown("<div class='video-container'>", unsafe_allow_html=True)
                st.video(p['video_url'])
                st.subheader(p['nombre_producto'])
                st.markdown(f"<p class='price-tag'>{p['precio']}$</p>", unsafe_allow_html=True)
                
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

        # Cálculo de Total
        prods_dict = {str(item['id']): item for item in prods.data}
        total = sum(prods_dict[k]['precio'] * v for k, v in st.session_state.carrito.items() if k in prods_dict)
        
        if total > 0:
            st.sidebar.markdown(f"## 🛒 Carrito\nTotal: **{total}$**")
            if st.sidebar.button("🏁 FINALIZAR COMPRA"):
                navegar("pago")
    else:
        st.warning("Esta tienda no tiene productos publicados.")
    
    st.button("🔙 VOLVER AL CENTRO COMERCIAL", on_click=navegar, args=("centro_comercial",))

# --- PÁGINA: PAGO Y FACTURA ---
elif st.session_state.pagina == "pago":
    tienda_nom = st.session_state.comercio_sel
    perfil = supabase.table("perfiles_comercio").select("*").eq("nombre_comercio", tienda_nom).single().execute()
    
    st.header("🏁 Facturación y Pago")
    
    with st.container():
        st.subheader("💳 Datos para el pago")
        st.info(perfil.data.get('datos_pago', 'Coordinar directamente por WhatsApp'))
        
        # Generar resumen
        resumen = ""
        total_final = 0
        productos_res = supabase.table("productos").select("*").eq("comercio_propietario", tienda_nom).execute()
        
        st.write("### Tu Pedido:")
        for pr in productos_res.data:
            id_p = str(pr['id'])
            if st.session_state.carrito.get(id_p, 0) > 0:
                c = st.session_state.carrito[id_p]
                subt = pr['precio'] * c
                total_final += subt
                resumen += f"✅ {pr['nombre_producto']} (x{c}) - {subt}$%0A"
                st.write(f"• {pr['nombre_producto']} x{c} = {subt}$")
        
        st.write(f"--- \n**TOTAL A PAGAR: {total_final}$**")
        
        # WhatsApp Link
        ws_num = perfil.data.get('whatsapp', '')
        mensaje_wa = f"*NUEVA ORDEN - D'UNIG*%0ATienda: {tienda_nom}%0A---%0A{resumen}---%0A*TOTAL: {total_final}$*"
        
        if st.button("📲 ENVIAR FACTURA POR WHATSAPP"):
            if ws_num:
                url_wa = f"https://wa.me/{ws_num}?text={mensaje_wa}"
                st.markdown(f'<a href="{url_wa}" target="_blank" style="background-color:#25D366;color:white;padding:15px;border-radius:10px;text-decoration:none;">Confirmar en WhatsApp</a>', unsafe_allow_html=True)
            else:
                st.error("El comercio no configuró su número de WhatsApp.")

    st.button("🔙 VOLVER A LA TIENDA", on_click=navegar, args=("vitrina_personal", tienda_nom))
