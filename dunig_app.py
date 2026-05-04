import streamlit as st
from supabase import create_client, Client
import random

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", initial_sidebar_state="collapsed")

# Conexión Segura a Supabase
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("⚠️ Error de conexión: Revisa tus Secrets en Streamlit Cloud.")
    st.stop()

# --- FUNCIÓN DE NAVEGACIÓN (Debe ir arriba para evitar NameError) ---
def navegar(destino, com=None):
    st.session_state.pagina = destino
    if com:
        st.session_state.comercio_sel = com
    st.rerun()

# Inicialización de estados de sesión
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None
if 'carrito' not in st.session_state: st.session_state.carrito = {}

# Estilos CSS Personalizados
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .stButton>button { border-radius: 10px; font-weight: bold; }
    .card-tienda { 
        border: 1px solid #D4AF37; 
        padding: 15px; 
        border-radius: 15px; 
        background: #1A1C23; 
        text-align: center;
        margin-bottom: 10px;
    }
    .price-tag { color: #D4AF37; font-size: 24px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA DE PÁGINAS (USANDO IF / ELIF)
# ==========================================

# --- PÁGINA: INICIO ---
if st.session_state.pagina == "inicio":
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.button("🛒 ENTRAR COMO CLIENTE", use_container_width=True, on_click=navegar, args=("centro_comercial",), key="btn_cliente")
    with col2:
        st.button("🏢 ACCESO PROPIETARIOS", use_container_width=True, on_click=navegar, args=("login_comercio",), key="btn_admin")

# --- PÁGINA: LOGIN PROPIETARIO ---
elif st.session_state.pagina == "login_comercio":
    st.subheader("🔑 Panel de Control de Negocio")
    nom_login = st.text_input("Nombre de tu Negocio", placeholder="Ej: Pizzería Dante")
    
    if st.button("INGRESAR AL PANEL", use_container_width=True):
        if nom_login:
            st.session_state.comercio_sesion = nom_login.strip()
            navegar("panel_carga")
        else:
            st.warning("Escribe el nombre de tu negocio.")
    
    st.button("🔙 VOLVER AL INICIO", on_click=navegar, args=("inicio",), key="back_login")

# --- PÁGINA: PANEL DE GESTIÓN (CARGA) ---
elif st.session_state.pagina == "panel_carga":
    nombre_c = st.session_state.comercio_sesion
    st.title(f"⚙️ Gestión: {nombre_c}")
    
    # SECCIÓN PERFIL
    with st.expander("🖼️ CONFIGURAR PERFIL (Logo, WhatsApp, Pago)"):
        logo = st.file_uploader("Logo del Negocio", type=['jpg', 'png', 'jpeg'])
        ws = st.text_input("WhatsApp (Ej: 584121234567)", help="Solo números con código de país")
        pago = st.text_area("Datos para el Pago (Zelle, Pago Móvil, etc.)")
        
        if st.button("Guardar Datos del Perfil"):
            try:
                url_l = None
                if logo:
                    path = f"logos/{nombre_c}_{random.randint(100,999)}.jpg"
                    supabase.storage.from_("fotos_productos").upload(path, logo.getvalue())
                    url_l = supabase.storage.from_("fotos_productos").get_public_url(path)
                
                data_perfil = {"nombre_comercio": nombre_c, "whatsapp": ws, "datos_pago": pago}
                if url_l: data_perfil["logo_url"] = url_l
                
                supabase.table("perfiles_comercio").upsert(data_perfil, on_conflict="nombre_comercio").execute()
                st.success("✅ Perfil guardado con éxito.")
            except Exception as e:
                st.error(f"Error al guardar perfil: {e}")

    # SECCIÓN CARGA PRODUCTO
    with st.form("form_carga_video", clear_on_submit=True):
        st.subheader("🎬 Publicar Video-Producto")
        p_nom = st.text_input("Nombre del Producto")
        p_pre = st.number_input("Precio ($)", min_value=0.0, format="%.2f")
        p_vid = st.file_uploader("Video (Máximo 10 segundos)", type=['mp4'])
        
        # El botón de formulario DEBE estar indentado aquí adentro
        submit = st.form_submit_button("🚀 PUBLICAR AHORA")
        
if st.form_submit_button("🚀 SUBIR PRODUCTO"):
            if p_nom and p_vid:
                try:
                    # 1. Limpiamos el nombre: quitamos espacios y caracteres raros
                    # Esto convierte "Cafetín Mérida" en "CafetinMerida"
                    nombre_limpio = "".join(e for e in p_nom if e.isalnum())
                    
                    # 2. Creamos el path seguro
                    path_v = f"productos/{nombre_limpio}_{random.randint(1000,9999)}.mp4"
                    
                    # 3. Subimos el archivo
                    supabase.storage.from_("fotos_productos").upload(path_v, p_vid.getvalue())
                    
                    # 4. Obtenemos la URL pública
                    url_v = supabase.storage.from_("fotos_productos").get_public_url(path_v)
                    
                    # 5. Insertamos en la tabla
                    supabase.table("productos").insert({
                        "nombre_producto": p_nom, 
                        "precio": p_pre, 
                        "video_url": url_v, 
                        "comercio_propietario": nombre_c
                    }).execute()
                    
                    st.success("¡Producto subido con éxito!")
                except Exception as e:
                    st.error(f"Error al subir: {e}")
            else:
                st.warning("Falta el nombre o el video.")

    st.write("---")
    st.button("🏠 CERRAR SESIÓN", on_click=navegar, args=("inicio",), key="logout")

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
                    # Validación de logo para evitar AttributeError
                    l_url = t.get('logo_url')
                    if l_url and l_url.strip() != "":
                        st.image(l_url, width=120)
                    else:
                        st.markdown("<h1 style='margin:0;'>🏪</h1>", unsafe_allow_html=True)
                    
                    st.subheader(t['nombre_comercio'])
                    if st.button("Ver Productos", key=f"entrar_{i}", use_container_width=True):
                        navegar("vitrina_personal", t['nombre_comercio'])
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No hay tiendas registradas todavía.")
    except Exception as e:
        st.error(f"Error al cargar: {e}")
        
    st.button("🔙 VOLVER", on_click=navegar, args=("inicio",), key="back_mall")

# --- PÁGINA: VITRINA PERSONALIZADA ---
elif st.session_state.pagina == "vitrina_personal":
    tienda = st.session_state.comercio_sel
    st.title(f"🏪 Vitrina: {tienda}")
    
    try:
        prods = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
        if prods.data:
            for p in prods.data:
                with st.container():
                    st.video(p['video_url'])
                    st.subheader(p['nombre_producto'])
                    st.markdown(f"<p class='price-tag'>{p['precio']}$</p>", unsafe_allow_html=True)
                    
                    # Sistema de Carrito
                    pid = str(p['id'])
                    cant = st.session_state.carrito.get(pid, 0)
                    c1, c2, c3 = st.columns([1,1,4])
                    if c1.button("➖", key=f"m_{pid}"):
                        st.session_state.carrito[pid] = max(0, cant - 1)
                        st.rerun()
                    c2.markdown(f"<h3 style='text-align:center;'>{cant}</h3>", unsafe_allow_html=True)
                    if c3.button("➕ Añadir al Carrito", key=f"p_{pid}", use_container_width=True):
                        st.session_state.carrito[pid] = cant + 1
                        st.rerun()
                    st.write("---")

            # Botón de Pago Flotante (si hay productos)
            total = 0
            # Crear diccionario para buscar precios rápido
            precios = {str(item['id']): item['precio'] for item in prods.data}
            for k, v in st.session_state.carrito.items():
                if k in precios: total += precios[k] * v
            
            if total > 0:
                if st.button(f"💳 FINALIZAR PEDIDO: {total}$", use_container_width=True, type="primary"):
                    navegar("pago")
        else:
            st.warning("Esta tienda no tiene productos disponibles.")
    except Exception as e:
        st.error(f"Error en vitrina: {e}")

    st.button("🔙 VOLVER AL CENTRO COMERCIAL", on_click=navegar, args=("centro_comercial",), key="back_vit")

# --- PÁGINA: PROCESAR PAGO ---
elif st.session_state.pagina == "pago":
    tienda = st.session_state.comercio_sel
    st.header("🏁 Finalizar Compra")
    
    try:
        p_res = supabase.table("perfiles_comercio").select("*").eq("nombre_comercio", tienda).single().execute()
        perfil = p_res.data
        
        st.info(f"📍 Pagando en: **{tienda}**")
        st.markdown(f"**Datos para tu transferencia:**\n\n{perfil.get('datos_pago', 'Consultar al vendedor')}")
        
        # --- NUEVA CASILLA: REFERENCIA BANCARIA ---
        num_referencia = st.text_input("🔢 Número de Referencia Bancaria", placeholder="Escribe el número de confirmación aquí")
        
        # Generar resumen para WhatsApp
        resumen = f"*NUEVO PEDIDO: {tienda}*%0A"
        resumen += f"---%0A"
        
        prods_res = supabase.table("productos").select("*").eq("comercio_propietario", tienda).execute()
        gran_total = 0
        for pr in prods_res.data:
            c_p = st.session_state.carrito.get(str(pr['id']), 0)
            if c_p > 0:
                resumen += f"✅ {pr['nombre_producto']} (x{c_p}): {pr['precio']*c_p}$%0A"
                gran_total += pr['precio']*c_p
        
        resumen += f"---%0A*TOTAL: {gran_total}$*%0A"
        
        # Agregar la referencia al mensaje de WhatsApp si existe
        if num_referencia:
            resumen += f"📌 *REF. BANCARIA:* {num_referencia}%0A"
        
        ws_vendedor = perfil.get('whatsapp', '')
        
        st.write("---")
        if st.button("🚀 ENVIAR PEDIDO Y COMPROBANTE", use_container_width=True, type="primary"):
            if not num_referencia:
                st.warning("⚠️ Por favor, anota el número de referencia antes de enviar.")
            else:
                # Link directo a WhatsApp
                link_wa = f"https://wa.me/{ws_vendedor}?text={resumen}"
                st.markdown(f"""
                    <a href="{link_wa}" target="_blank" style="text-decoration:none;">
                        <div style="background-color:#25d366;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:bold;">
                            CLICK AQUÍ PARA CONFIRMAR EN WHATSAPP
                        </div>
                    </a>
                """, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error al procesar el pago: {e}")
    
    st.button("🔙 REGRESAR A VITRINA", on_click=navegar, args=("vitrina_personal", tienda))
