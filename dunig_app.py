import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    # Asegúrate de tener estos secrets en .streamlit/secrets.toml
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def obtener_cuentas_admin():
    try:
        res = supabase.table("ajustes_sistema").select("valor").eq("clave", "cuentas_activacion").execute()
        return res.data[0]['valor'] if res.data else "⚠️ Cuentas de activación no configuradas."
    except:
        return "❌ Error al conectar con los ajustes del sistema."

# Constantes del Sistema
PLANES_LIMITES = {"GRATUITO": 3, "BRONCE": 10, "PLATA": 25, "ORO": 9999}

OPCIONES_PLAN_VISUAL = {
    "GRATUITO": "⚪ GRATUITO (Básico - 3 Productos)",
    "BRONCE": "🥉 BRONCE (Emprendedor - 10 Productos)",
    "PLATA": "🥈 PLATA (Crecimiento - 25 Productos)",
    "ORO": "👑 ORO (Ilimitado - Ventas Premium)"
}

# Gestión de Vistas y Estado de Sesión
if 'view' not in st.session_state: 
    st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False
if 'user_email' not in st.session_state: 
    st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    
    /* Botones Dorados Luxury */
    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        color: #000 !important; border-radius: 30px !important;
        font-weight: 800 !important; text-transform: uppercase;
        border: none !important;
    }

    /* Portadas CUADRADAS con esquinas OVALADAS para el MALL */
    .img-mall-luxury {
        width: 100%;
        aspect-ratio: 1 / 1; 
        object-fit: cover; 
        border-radius: 25px;
        border: 2px solid #D4AF37;
        box-shadow: 0px 4px 15px rgba(212, 175, 55, 0.3);
        margin-bottom: 10px;
    }

    .price-bubble {
        position: absolute; top: 15px; right: 15px;
        background: rgba(0, 0, 0, 0.85); color: #39FF14; 
        padding: 5px 15px; border-radius: 50px;
        font-weight: 900; border: 2px solid #39FF14; z-index: 10;
    }

    .benefit-card {
        background: rgba(255,255,255,0.05);
        padding: 10px;
        border-radius: 15px;
        border: 1px solid #D4AF37;
        text-align: center;
        font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. DIÁLOGOS DE INTERFAZ
# ==========================================
@st.dialog("💎 CARRITO D'UNIG LUXURY")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    st.metric("TOTAL A PAGAR", f"${total:,.2f}")
    st.divider()
    st.info(f"💳 **DATOS DE PAGO:**\n{tienda.get('datos_pago', 'Consultar al vendedor')}")
    ref = st.text_input("Ingrese Ref. de Pago")
    if st.button("🚀 CONFIRMAR PEDIDO"):
        if ref:
            msj = f"✨ *PEDIDO LUXURY*\n📦 *Producto:* {producto['nombre_producto']}\n🔢 *Cant:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            tel = str(tienda['whatsapp']).replace("+", "").strip()
            st.link_button("ENVIAR POR WHATSAPP", f"https://wa.me/{tel}?text={urllib.parse.quote(msj)}")
        else:
            st.error("Por favor, ingrese la referencia de pago")

# ==========================================
# 4. FUNCIONES DE GESTIÓN (ADMIN)
# ==========================================
@st.dialog("📝 EDITAR COMERCIO")
def editar_comercio_dialog(comercio):
    st.write(f"Editando: **{comercio['nombre_comercio']}**")
    
    # --- CORRECCIÓN VALUERROR selector 'Plan' ---
    lista_planes_claves = list(PLANES_LIMITES.keys()) # ['GRATUITO', 'BRONCE', etc.]
    plan_actual_db = comercio.get('plan') # Valor que viene de Supabase

    # Validamos si el plan de la DB existe en nuestra lista de constantes.
    # Si no existe (es None o está mal escrito), usamos 'GRATUITO' por defecto.
    plan_para_selector = plan_actual_db if plan_actual_db in lista_planes_claves else lista_planes_claves[0]
    
    # Obtenemos el índice numérico para el selector
    indice_defecto = lista_planes_claves.index(plan_para_selector)

    # Inputs de edición
    nuevo_whatsapp = st.text_input("WhatsApp", value=comercio.get('whatsapp', ''))
    
    nuevo_plan = st.selectbox(
        "Plan de Socio", 
        options=lista_planes_claves, 
        index=indice_defecto,
        format_func=lambda x: OPCIONES_PLAN_VISUAL.get(x, x)
    )

    if st.button("GUARDAR CAMBIOS EN SOCIO"):
        if nuevo_whatsapp:
            try:
                supabase.table("perfiles_comercio").update({
                    "whatsapp": nuevo_whatsapp, 
                    "plan": nuevo_plan
                }).eq("id", comercio['id']).execute()
                st.success("¡Datos actualizados correctamente!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar en la base de datos: {e}")
        else:
            st.error("El campo WhatsApp no puede estar vacío.")

def borrar_comercio_completo(comercio_id, nombre_comercio):
    """
    Realiza un borrado 'En Cascada' manual desde Python.
    Primero borra productos y luego el comercio para evitar errores de clave externa.
    """
    with st.spinner(f"Eliminando {nombre_comercio} y todos sus productos..."):
        try:
            # 1. Borrar todos los productos asociados primero
            # (Limpiamos la tabla 'hija')
            supabase.table("productos").delete().eq("comercio_relacionado", nombre_comercio).execute()
            
            # 2. Borrar el perfil del comercio
            # (Limpiamos la tabla 'padre')
            resultado = supabase.table("perfiles_comercio").delete().eq("id", comercio_id).execute()
            
            if resultado.data:
                st.toast(f"✅ Comercio {nombre_comercio} eliminado definitivamente.", icon="🗑️")
                st.rerun()
            else:
                st.error("El comercio no se pudo eliminar (quizás ya no existe).")
        
        except Exception as e:
            st.error(f"⚠️ Error crítico durante el borrado: {e}")
            st.info("Verifica las restricciones de clave externa (Foreign Keys) en Supabase si el problema persiste.")

# ==========================================
# 5. LÓGICA DE VISTAS (NAVEGACIÓN)
# ==========================================
es_admin_master = st.query_params.get("admin") == "true"
es_vía_registro = st.query_params.get("reg") == "true"

# --- VISTA: REGISTRO DE SOCIO ---
if es_vía_registro:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>✨ REGISTRO DE SOCIO</h1>", unsafe_allow_html=True)
    
    st.markdown("### 🏆 BENEFICIOS DEL CLUB")
    b1, b2, b3, b4 = st.columns(4)
    with b1: st.markdown("<div class='benefit-card'>⚪<br><b>GRATIS</b><br>3 Prods</div>", unsafe_allow_html=True)
    with b2: st.markdown("<div class='benefit-card'>🥉<br><b>BRONCE</b><br>10 Prods</div>", unsafe_allow_html=True)
    with b3: st.markdown("<div class='benefit-card'>🥈<br><b>PLATA</b><br>25 Prods</div>", unsafe_allow_html=True)
    with b4: st.markdown("<div class='benefit-card'>👑<br><b>ORO</b><br>Ilimitado</div>", unsafe_allow_html=True)

    with st.expander("💳 CUENTAS PARA ACTIVACIÓN", expanded=False):
        st.markdown(obtener_cuentas_admin())

    with st.form("form_reg_externo", clear_on_submit=True):
        st.write("Datos de tu comercio")
        r_nombre_tienda = st.text_input("Nombre de la Tienda")
        r_email = st.text_input("Email del Propietario").lower().strip()
        r_whatsapp = st.text_input("WhatsApp (Ej: 58412...)")
        plan_seleccionado = st.selectbox("Selecciona tu Plan", options=list(PLANES_LIMITES.keys()), format_func=lambda x: OPCIONES_PLAN_VISUAL[x])
        r_foto_portada = st.file_uploader("Foto de Portada", type=['jpg', 'png'])
        r_referencia_pago = st.text_input("Referencia de Pago")

        if st.form_submit_button("SOLICITAR REGISTRO DE COMERCIO"):
            if r_nombre_tienda and r_email and r_whatsapp and r_foto_portada and r_referencia_pago:
                # Subir Imagen de Portada
                path_portada = f"portadas/reg_{random.randint(1000,9999)}_{r_foto_portada.name}"
                supabase.storage.from_("fotos_productos").upload(path_portada, r_foto_portada.getvalue())
                url_portada_final = supabase.storage.from_("fotos_productos").get_public_url(path_portada)
                
                # Crear Perfil (Inactivo por defecto)
                supabase.table("perfiles_comercio").insert({
                    "nombre_comercio": r_nombre_tienda, 
                    "email_propietario": r_email, 
                    "whatsapp": r_whatsapp, 
                    "portada_url": url_portada_final, 
                    "plan": plan_seleccionado, 
                    "codigo_acceso": f"LUX{random.randint(10,99)}",
                    "activo": False # Esperando activación del admin
                }).execute()
                st.success("¡Registro Exitoso! Tu tienda está en proceso de activación. Te contactaremos pronto.")
            else:
                st.error("Por favor, completa todos los campos obligatorios y sube tu foto.")

# --- VISTA: MALL PÚBLICO (No Admin) ---
elif not es_admin_master:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        
        # Solo mostrar tiendas activas
        try:
            tiendas = supabase.table("perfiles_comercio").select("*").eq("activo", True).execute().data
        except:
            tiendas = [] # Manejo de error si la columna 'activo' no existe aún
            tiendas = supabase.table("perfiles_comercio").select("*").execute().data

        if not tiendas:
            st.info("Próximamente nuevas tiendas de lujo...")
        
        # GALERÍA DE 2 EN 2
        for i in range(0, len(tiendas), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(tiendas):
                    t = tiendas[i + j]
                    with cols[j]:
                        # Protección anti-error si no hay imagen
                        if t.get("portada_url"):
                            st.markdown(f'<img src="{t["portada_url"]}" class="img-mall-luxury">', unsafe_allow_html=True)
                        else:
                            st.markdown('<div style="width:100%; aspect-ratio:1/1; background:#333; border-radius:25px; display:flex; align-items:center; justify-content:center; color:#D4AF37; border:2px solid #D4AF37;">🖼️ Sin Portada</div>', unsafe_allow_html=True)
                            
                        st.markdown(f"<p style='text-align:center; color:#D4AF37; font-weight:bold; margin-top:-5px;'>{t['nombre_comercio'].upper()}</p>", unsafe_allow_html=True)
                        
                        if st.button("VISITAR TIENDA", key=f"mall_vis_{t['id']}", use_container_width=True):
                            st.session_state.tienda_actual = t
                            ir_a('tienda')

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER AL MALL"): ir_a('mall')
        
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute().data
        
        if not prods:
            st.info("Esta tienda está preparando su próxima colección.")
            
        for p in prods:
            with st.container():
                # Burbuja de Precio flotante
                st.markdown(f"<div style='position: relative;'><div class='price-bubble'>${p['precio']}</div></div>", unsafe_allow_html=True)
                
                # Video del producto (Autoplay)
                st.video(p['video_url'], autoplay=True, loop=True, muted=True)
                
                if st.button(f"🛒 COMPRAR {p['nombre_producto']}", key=f"btn_compra_{p['id']}", use_container_width=True):
                    ventana_pago(p, t)

# --- VISTA: PANEL DE CONTROL (Socios y Admin) ---
else:
    st.markdown("<h1 style='text-align:center; color:#D4AF37;'>⚙️ PANEL DE CONTROL</h1>", unsafe_allow_html=True)
    
    # 1. Login de Socio
    if not st.session_state.logged_in:
        with st.container(border=True):
            st.write("Acceso para Socios")
            l_email = st.text_input("Email de Propietario").strip().lower()
            l_codigo = st.text_input("Código de Acceso", type="password").strip().upper()
            
            if st.button("🔓 ENTRAR AL PANEL"):
                res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", l_email).execute()
                
                if res.data and str(res.data[0].get('codigo_acceso', '')).upper() == l_codigo:
                    st.session_state.logged_in = True
                    st.session_state.user_email = l_email
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Verifica tu email y código.")
    
    # 2. Panel Activo
    else:
        # Obtener perfil del socio logueado
        perfil_socio = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute().data[0]
        
        # Calcular capacidad de productos
        count_productos = supabase.table("productos").select("id", count="exact").eq("comercio_relacionado", perfil_socio['nombre_comercio']).execute()
        cant_actual = count_productos.count or 0
        
        nombre_plan_actual = perfil_socio.get('plan', 'GRATUITO')
        cant_limite = PLANES_LIMITES.get(nombre_plan_actual, 3)
        
        # Header del Panel
        col_h1, col_h2 = st.columns([3, 1])
        col_h1.write(f"Bienvenido socio: **{perfil_socio['nombre_comercio']}**")
        col_h2.write(f"Plan: **{nombre_plan_actual}**")
        
        st.progress(min(cant_actual / cant_limite, 1.0))
        st.caption(f"Capacidad utilizada: {cant_actual} de {cant_limite} productos permitidos.")

        # Pestañas de Gestión
        pestanas = ["➕ AGREGAR PRODUCTO", "📦 GESTIÓN DE CATÁLOGO", "💳 DATOS DE PAGO"]
        
        # Si es el Dueño Principal (TÚ), agregar pestaña maestra
        es_admin_general = perfil_socio['nombre_comercio'].upper() == "D'UNIG LUXURY" # AJUSTA ESTE NOMBRE A TU TIENDA PRINCIPAL
        if es_admin_general:
            pestanas.append("🏙️ GESTIÓN MAESTRA (COMERCIOS)")
            
        t1, t2, t3, *t4_list = st.tabs(pestanas)
        
        # TAB 1: AGREGAR
        with t1:
            if cant_actual < cant_limite:
                st.subheader("Publicar Nuevo Producto")
                with st.form("form_add_producto", clear_on_submit=True):
                    add_nombre = st.text_input("Nombre del Producto (Ej: Reloj Rolex Datejust)")
                    add_precio = st.number_input("Precio de Venta ($)", min_value=0.0, step=1.0)
                    add_video = st.file_uploader("Video Exclusivo (MP4)", type=['mp4'])
                    
                    if st.form_submit_button("🚀 PUBLICAR EN EL MALL"):
                        if add_nombre and add_precio > 0 and add_video:
                            with st.spinner("Subiendo video de lujo..."):
                                # Subir Video a Storage
                                fname_video = f"videos/{perfil_socio['nombre_comercio']}_{random.randint(1000,9999)}.mp4"
                                supabase.storage.from_("fotos_productos").upload(
                                    fname_video, 
                                    add_video.getvalue(), 
                                    {"content-type": "video/mp4"}
                                )
                                url_video_final = supabase.storage.from_("fotos_productos").get_public_url(fname_video)
                                
                                # Insertar en Tabla Productos
                                supabase.table("productos").insert({
                                    "nombre_producto": add_nombre, 
                                    "precio": add_precio, 
                                    "video_url": url_video_final, 
                                    "comercio_relacionado": perfil_socio['nombre_comercio']
                                }).execute()
                                
                                st.success(f"¡{add_nombre} ya está en línea!")
                                st.rerun()
                        else:
                            st.error("Por favor completa el nombre, precio y sube un video MP4.")
            else:
                st.warning("⚠️ Has alcanzado el límite de productos de tu plan actual. Mejora tu plan para subir más.")

        # TAB 2: GESTIÓN
        with t2:
            st.subheader("Catálogo Actual")
            productos_socio = supabase.table("productos").select("*").eq("comercio_relacionado", perfil_socio['nombre_comercio']).execute().data
            
            if not productos_socio:
                st.info("Tu catálogo está vacío. ¡Agrega tu primer producto de lujo!")
                
            for it in productos_socio:
                with st.container(border=True):
                    col_det1, col_det2 = st.columns([3, 1])
                    col_det1.write(f"**{it['nombre_producto']}**")
                    col_det1.write(f"Precio: ${it['precio']}")
                    
                    if col_det2.button("🗑️ Eliminar", key=f"del_prod_{it['id']}", use_container_width=True):
                        # Nota: Aquí también podrías borrar el video del storage si quisieras.
                        supabase.table("productos").delete().eq("id", it['id']).execute()
                        st.toast(f"Producto eliminado.")
                        st.rerun()

        # TAB 3: PAGOS
        with t3:
            st.subheader("Configuración de Pago para Clientes")
            instrucciones_pago = st.text_area(
                "Escribe aquí las cuentas bancarias, Zelle, Pago Móvil o instrucciones para que el cliente finalice la compra.", 
                value=perfil_socio.get('datos_pago','') or "",
                height=150
            )
            
            if st.button("💾 GUARDAR DATOS DE PAGO"):
                supabase.table("perfiles_comercio").update({
                    "datos_pago": instrucciones_pago
                }).eq("id", perfil_socio['id']).execute()
                st.success("Tus datos de pago se han actualizado.")

        # TAB 4: GESTIÓN MAESTRA (SOLO ADMIN GENERAL)
        if es_admin_general and t4_list:
            t4 = t4_list[0] # Obtener la pestaña si existe
            with t4:
                st.subheader("Panel de Control de Comercios Socios")
                
                # Obtener todos los comercios
                todos_comercios = supabase.table("perfiles_comercio").select("*").execute().data
                
                # Barra de búsqueda rápida
                busqueda = st.text_input("🔍 Buscar comercio por nombre o email").lower().strip()
                
                for c in todos_comercios:
                    # Filtrado de búsqueda
                    if busqueda and busqueda not in c['nombre_comercio'].lower() and busqueda not in c['email_propietario'].lower():
                        continue
                        
                    # Contenedor para cada comercio
                    with st.container(border=True):
                        col_c1, col_c2, col_c3, col_c4 = st.columns([1, 2, 1, 1])
                        
                        # Protección anti-error de imagen
                        if c.get('portada_url'):
                            col_c1.image(c['portada_url'], width=60)
                        else:
                            col_c1.write("🖼️❌")
                            
                        # Info Principal
                        col_c2.write(f"**{c['nombre_comercio']}**")
                        col_c2.caption(f"📧 {c['email_propietario']}")
                        col_c2.caption(f"💎 Plan: {c.get('plan','S/N')} | 🔑 Código: {c.get('codigo_acceso', 'XXXX')}")
                        
                        # Estado Activo/Inactivo
                        estado_actual = c.get('activo', True) # Asumimos True si no existe columna
                        col_c2.write("Estado: ✅ Activo" if estado_actual else "Estado: 🔴 Inactivo")

                        # Botón: EDITAR
                        if col_c3.button("📝 Editar", key=f"master_ed_{c['id']}", use_container_width=True):
                            editar_comercio_dialog(c)
                            
                        # Botón: ELIMINAR DEFINITIVO
                        if col_c4.button("🗑️ Borrar", key=f"master_del_{c['id']}", use_container_width=True):
                            # Usamos un mensaje de confirmación previo (toast)
                            st.warning(f"¿Estás seguro de eliminar {c['nombre_comercio']}? Se borrarán TODOS sus productos.")
                            # Si vuelve a presionar, se borra (Streamlit re-ejecuta el botón)
                            # Para hacerlo directo, llamamos a la función:
                            borrar_comercio_completo(c['id'], c['nombre_comercio'])

        # Botón general de cerrar sesión
        st.divider()
        if st.button("🚪 CERRAR SESIÓN DEL PANEL"):
            st.session_state.logged_in = False
            st.session_state.user_email = None
            st.rerun()