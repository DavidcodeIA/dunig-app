import streamlit as st
from supabase import create_client, Client
import random

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="D'UNIG PLATINUM", layout="wide", page_icon="⚜️")

# --- 2. CONEXIÓN A SUPABASE ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("Error de conexión. Revisa tus st.secrets.")
    st.stop()

# --- 3. GESTIÓN DE ESTADOS ---
if 'pagina' not in st.session_state: st.session_state.pagina = "inicio"
if 'comercio_sesion' not in st.session_state: st.session_state.comercio_sesion = None
if 'comercio_sel' not in st.session_state: st.session_state.comercio_sel = None
if 'carrito' not in st.session_state: st.session_state.carrito = {}

def navegar(destino, com=None):
    st.session_state.pagina = destino
    if com:
        st.session_state.comercio_sel = com
    st.rerun()

# --- 4. ESTILOS VISUALES ---
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .stButton>button { border-radius: 10px; }
    .tienda-card { 
        border: 1px solid #D4AF37; 
        padding: 20px; 
        border-radius: 15px; 
        background-color: #1A1C23; 
        text-align: center;
        margin-bottom: 20px;
    }
    .video-box { 
        border-bottom: 1px solid #333; 
        margin-bottom: 25px; 
        padding-bottom: 15px; 
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# ESTRUCTURA DE PÁGINAS
# ==========================================

# --- PÁGINA: INICIO ---
if st.session_state.pagina == "inicio":
    st.markdown("<h1 style='text-align:center;'>⚜️ D'UNIG PLATINUM ⚜️</h1>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 ENTRAR COMO CLIENTE", use_container_width=True):
            navegar("centro_comercial")
    with col2:
        if st.button("🏢 ACCESO PROPIETARIOS", use_container_width=True):
            navegar("login_comercio")

# --- PÁGINA: LOGIN PROPIETARIO ---
elif st.session_state.pagina == "login_comercio":
    st.title("🔑 Acceso al Panel")
    nombre_login = st.text_input("Nombre de tu Negocio")
    if st.button("INGRESAR"):
        if nombre_login:
            st.session_state.comercio_sesion = nombre_login
            navegar("panel_carga")
    if st.button("🔙 VOLVER"): navegar("inicio")

# --- PÁGINA: PANEL DE CONTROL ---
elif st.session_state.pagina == "panel_carga":
    mi_tienda = st.session_state.comercio_sesion
    st.title(f"⚙️ Panel de {mi_tienda}")

    # CONFIGURACIÓN DE PERFIL
    with st.expander("🖼️ CONFIGURAR MI VITRINA (Logo, WhatsApp, Pago)"):
        logo_file = st.file_uploader("Subir Logo", type=['jpg', 'png'])
        whatsapp_input = st.text_input("Número WhatsApp (ej: 584120000000)")
        pago_info = st.text_area("Datos para que el cliente te pague")
        
        if st.button("Guardar Cambios de Perfil"):
            try:
                final_logo_url = None
                if logo_file:
                    file_path = f"logos/{mi_tienda}_{random.randint(100,999)}.jpg"
                    supabase.storage.from_("fotos_productos").upload(file_path, logo_file.getvalue())
                    final_logo_url = supabase.storage.from_("fotos_productos").get_public_url(file_path)
                
                datos_upsert = {
                    "nombre_comercio": mi_tienda,
                    "whatsapp": whatsapp_input,
                    "datos_pago": pago_info
                }
                if final_logo_url: datos_upsert["logo_url"] = final_logo_url
                
                supabase.table("perfiles_comercio").upsert(datos_upsert, on_conflict="nombre_comercio").execute()
                st.success("✅ ¡Perfil actualizado!")
            except Exception as e:
                st.error(f"Error: {e}")

if st.form_submit_button("🚀 SUBIR PRODUCTO"):
            if nom_prod and vid_prod:
                try:
                    # 1. Limpiar nombre para evitar errores de caracteres
                    nombre_limpio = "".join(filter(str.isalnum, mi_tienda))
                    vid_path = f"productos/{nombre_limpio}_{random.randint(1000,9999)}.mp4"
                    
                    # 2. Intentar subir
                    bytes_data = vid_prod.getvalue()
                    res = supabase.storage.from_("fotos_productos").upload(vid_path, bytes_data)
                    
                    # 3. Obtener URL
                    vid_url = supabase.storage.from_("fotos_productos").get_public_url(vid_path)
                    
                    # 4. Guardar en tabla
                    supabase.table("productos").insert({
                        "nombre_producto": nom_prod,
                        "precio": pre_prod,
                        "video_url": vid_url,
                        "comercio_propietario": mi_tienda
                    }).execute()
                    
                    st.success("✅ ¡Video publicado con éxito!")
                except Exception as e:
                    # Esto nos dirá el error real (si es permiso o bucket)
                    st.error(f"Error técnico: {e}")
            else:
                st.warning("Escribe un nombre y selecciona un video.")

# --- PÁGINA: CENTRO COMERCIAL ---
elif st.session_state.pagina == "centro_comercial":
    st.title("🏢 CENTRO COMERCIAL D'UNIG")
    try:
        res_tiendas = supabase.table("perfiles_comercio").select("*").execute()
        if res_tiendas.data:
            columnas = st.columns(3)
            for i, tienda in enumerate(res_tiendas.data):
                with columnas[i % 3]:
                    st.markdown("<div class='tienda-card'>", unsafe_allow_html=True)
                    url_logo = tienda.get('logo_url')
                    if url_logo:
                        st.image(url_logo, width=100)
                    else:
                        st.markdown("<h1>🏪</h1>", unsafe_allow_html=True)
                    
                    st.subheader(tienda['nombre_comercio'])
                    if st.button(f"Entrar a {tienda['nombre_comercio']}", key=f"btn_{i}"):
                        navegar("vitrina_personal", tienda['nombre_comercio'])
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No hay tiendas registradas aún.")
    except Exception as e:
        st.error(f"Error al cargar: {e}")
    
    if st.button("🔙 VOLVER AL INICIO"): navegar("inicio")

# --- PÁGINA: VITRINA PERSONAL ---
elif st.session_state.pagina == "vitrina_personal":
    nombre_t = st.session_state.comercio_sel
    st.title(f"🏪 Tienda: {nombre_t}")
    
    try:
        res_p = supabase.table("productos").select("*").eq("comercio_propietario", nombre_t).execute()
        if res_p.data:
            for p in res_p.data:
                with st.container():
                    st.markdown("<div class='video-box'>", unsafe_allow_html=True)
                    st.video(p['video_url'])
                    st.subheader(f"{p['nombre_producto']} - ${p['precio']}")
                    
                    # Carrito Suma/Resta
                    p_id = str(p['id'])
                    cant = st.session_state.carrito.get(p_id, 0)
                    c1, c2, c3 = st.columns([1,1,4])
                    if c1.button("➖", key=f"m_{p_id}"):
                        st.session_state.carrito[p_id] = max(0, cant - 1)
                        st.rerun()
                    c2.write(f"### {cant}")
                    if c3.button("➕", key=f"p_{p_id}"):
                        st.session_state.carrito[p_id] = cant + 1
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

            # Cálculo de Total
            dict_precios = {str(item['id']): item['precio'] for item in res_p.data}
            total_compra = sum(dict_precios[k] * v for k, v in st.session_state.carrito.items() if k in dict_precios)
            
            if total_compra > 0:
                st.write("---")
                if st.button(f"💳 FINALIZAR COMPRA: ${total_compra}", use_container_width=True):
                    navegar("pago")
        else:
            st.warning("Esta tienda no tiene productos cargados.")
    except Exception as e:
        st.error(f"Error: {e}")

    if st.button("🔙 VOLVER AL CENTRO"): navegar("centro_comercial")

# --- PÁGINA: PAGO ---
elif st.session_state.pagina == "pago":
    t_pago = st.session_state.comercio_sel
    st.header(f"🏁 Checkout - {t_pago}")
    
    try:
        perfil_t = supabase.table("perfiles_comercio").select("*").eq("nombre_comercio", t_pago).single().execute()
        st.subheader("Método de Pago del Vendedor:")
        st.success(perfil_t.data.get('datos_pago', "Consultar al WhatsApp"))
        
        # Generar mensaje WhatsApp
        lista_pedido = ""
        monto_total = 0
        all_p = supabase.table("productos").select("*").eq("comercio_propietario", t_pago).execute()
        
        for item in all_p.data:
            c = st.session_state.carrito.get(str(item['id']), 0)
            if c > 0:
                sub = item['precio'] * c
                lista_pedido += f"- {item['nombre_producto']} x{c} (${sub})%0A"
                monto_total += sub
        
        msg = f"*NUEVO PEDIDO D'UNIG*%0A---%0A{lista_pedido}---%0A*TOTAL: ${monto_total}*"
        num_ws = perfil_t.data.get('whatsapp', '')

        if st.button("📲 ENVIAR PEDIDO POR WHATSAPP"):
            st.markdown(f'<a href="https://wa.me/{num_ws}?text={msg}" target="_blank">Click aquí para abrir WhatsApp</a>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error en el pago: {e}")
        
    if st.button("🔙 VOLVER A LA VITRINA"): navegar("vitrina_personal", t_pago)
