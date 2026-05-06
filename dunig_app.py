import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN DE ALTO RENDIMIENTO & MARCA
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def init_connection():
    # Optimización: Conexión persistente para respuesta instantánea
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

PLANES = {
    "BRONCE": 5,
    "PLATINUM": 15,
    "DIAMANTE": 50
}

# --- SISTEMA DE RUTAS INTELIGENTE ---
query_params = st.query_params
es_admin = query_params.get("admin") == "true"

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'tienda_actual' not in st.session_state: st.session_state.tienda_actual = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. UI/UX: ESTÉTICA LUXURY AVANZADA (OPCIÓN 5)
# ==========================================
st.markdown("""
    <style>
    /* Fondo con degradado radial para profundidad */
    .main { 
        background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); 
        color: #ffffff; 
    }
    
    /* Animación Shimmer para botones dorados */
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    .stButton>button {
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        background-size: 200% 100% !important;
        animation: shimmer 5s infinite linear !important;
        color: #000 !important;
        border-radius: 30px !important;
        border: none !important;
        font-weight: 800 !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase;
        transition: 0.4s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(212, 175, 55, 0.5);
    }

    /* Tarjetas Glassmorphism */
    .luxury-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    /* Burbuja Neón de Precio */
    .price-bubble {
        position: absolute;
        top: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.9);
        color: #39FF14; 
        padding: 8px 20px;
        border-radius: 50px;
        font-weight: 900;
        font-size: 1.4rem;
        border: 2px solid #39FF14;
        box-shadow: 0 0 15px rgba(57, 255, 20, 0.5);
        z-index: 10;
    }

    /* Ocultar elementos nativos para Marca Blanca */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. COMPONENTES: CARRITO & BUSCADOR
# ==========================================
@st.dialog("💎 CARRITO D'UNIG LUXURY")
def ventana_pago(producto, tienda):
    st.markdown(f"### ✨ {producto['nombre_producto']}")
    col_cant, col_total = st.columns(2)
    cantidad = col_cant.number_input("Cantidad", min_value=1, value=1)
    total = float(producto['precio']) * cantidad
    col_total.metric("TOTAL", f"${total:,.2f}")
    
    st.divider()
    st.info(f"💳 **MÉTODO DE PAGO:**\n\n{tienda.get('datos_pago', 'Consultar con vendedor')}")
    ref = st.text_input("Número de Referencia", placeholder="Ej: 987654321")
    
    if st.button("🚀 CONFIRMAR PEDIDO", use_container_width=True):
        if ref:
            msj = f"✨ *PEDIDO D'UNIG LUXURY*\n🏪 *Tienda:* {tienda['nombre_comercio']}\n📦 *Prod:* {producto['nombre_producto']}\n🔢 *Cant:* {cantidad}\n💰 *Total:* ${total}\n🎫 *Ref:* {ref}"
            st.link_button("ABRIR WHATSAPP", f"https://wa.me/{tienda['whatsapp']}?text={urllib.parse.quote(msj)}")
        else:
            st.error("Por favor, ingresa el número de referencia.")

# ==========================================
# 4. PANELES DIVIDIDOS (SHOPPING vs ADMIN)
# ==========================================

# --- PANEL CLIENTES: D'UNIG LUXURY SHOPPING ---
if not es_admin:
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        
        # Opción 2: Buscador de comercios
        busqueda = st.text_input("🔍 Buscar tiendas o categorías...", placeholder="Ej: Ropa, Joyería...")
        
        res = supabase.table("perfiles_comercio").select("*").execute()
        tiendas = [t for t in res.data if busqueda.lower() in t['nombre_comercio'].lower()]
        
        cols = st.columns(2)
        for idx, t in enumerate(tiendas):
            with cols[idx % 2]:
                st.markdown(f"<div class='luxury-card'>", unsafe_allow_html=True)
                st.markdown(f"<h3 style='text-align:center;'>{t['nombre_comercio'].upper()}</h3>", unsafe_allow_html=True)
                if st.button("VISITAR", key=f"t_{t['id']}", use_container_width=True):
                    st.session_state.tienda_actual = t
                    ir_a('tienda')
                st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        st.button("⬅️ VOLVER AL MALL", on_click=ir_a, args=('mall',))
        
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        
        for p in prods.data:
            st.markdown(f"<div style='position: relative;'><div class='price-bubble'>${p['precio']}</div></div>", unsafe_allow_html=True)
            st.video(p['video_url'])
            if st.button(f"🛒 ADQUIRIR {p['nombre_producto']}", key=f"p_{p['id']}", use_container_width=True):
                ventana_pago(p, t)
            st.divider()

# --- NUEVA ESTRUCTURA DE PESTAÑAS AUTÓNOMAS ---
            tab1, tab2, tab3, tab4 = st.tabs(["➕ AGREGAR", "📦 GESTIONAR", "💳 PAGOS", "💎 MI PLAN"])

            with tab1: # AGREGAR PRODUCTO (OPCIÓN 1: CON VALIDACIÓN)
                if total_p >= limite: 
                    st.error("Límite de plan alcanzado. Sube de nivel en la pestaña 'MI PLAN'.")
                else:
                    with st.form("new_p", clear_on_submit=True):
                        n = st.text_input("Nombre del Producto")
                        p = st.number_input("Precio ($)", min_value=0.0)
                        v = st.file_uploader("Video publicitario (MP4)", type=['mp4'])
                        if st.form_submit_button("🚀 PUBLICAR EN LUXURY MALL"):
                            if n and v:
                                v_path = f"videos/{perf['id']}_{random.randint(1000,9999)}.mp4"
                                supabase.storage.from_("fotos_productos").upload(v_path, v.getvalue())
                                v_url = supabase.storage.from_("fotos_productos").get_public_url(v_path)
                                supabase.table("productos").insert({
                                    "nombre_producto": n, "precio": p, "video_url": v_url, 
                                    "comercio_relacionado": perf['nombre_comercio']
                                }).execute()
                                st.rerun()

            with tab2: # GESTIONAR INVENTARIO
                items = supabase.table("productos").select("*").eq("comercio_relacionado", perf['nombre_comercio']).execute()
                for i in items.data:
                    with st.expander(f"📝 {i['nombre_producto']} - ${i['precio']}"):
                        if st.button("🗑️ ELIMINAR", key=f"del_{i['id']}"):
                            supabase.table("productos").delete().eq("id", i['id']).execute()
                            st.rerun()

            with tab3: # CONFIGURACIÓN DE COBRO (CLIENTES)
                st.markdown("#### 💳 Cómo te pagan tus clientes")
                pago_info = st.text_area("Instrucciones de Pago Móvil / Transferencia", value=str(perf.get('datos_pago', '')))
                if st.button("💾 GUARDAR MÉTODO DE COBRO"):
                    supabase.table("perfiles_comercio").update({"datos_pago": pago_info}).eq("id", perf['id']).execute()
                    st.success("Configuración de cobro actualizada.")

            with tab4: # 💎 MI PLAN (AUTOGESTIÓN DE PAGOS A D'UNIG LUXURY)
                st.markdown("### 🏆 Membresía D'UNIG LUXURY")
                precios = {"BRONCE": "Gratis", "PLATINUM": "29.99", "DIAMANTE": "99.99"}
                
                col_p, col_c = st.columns(2)
                col_p.metric("Tu Plan", plan)
                col_c.metric("Costo Mensual", f"${precios.get(plan, '0.00')} USD")

                st.divider()
                st.markdown("#### ✨ Mejora tu presencia")
                c1, c2 = st.columns(2)
                
                with c1:
                    st.markdown("**PLAN PLATINUM**\n* 15 Productos\n* Soporte 24/7\n* Sello Verificado")
                    st.link_button("💎 PAGAR PLATINUM", "https://tu-link-de-pago.com/platinum") # Reemplazar con tu link real

                with c2:
                    st.markdown("**PLAN DIAMANTE**\n* Productos Ilimitados\n* Destacado VIP\n* Video 4K")
                    st.link_button("👑 PAGAR DIAMANTE", "https://tu-link-de-pago.com/diamante") # Reemplazar con tu link real

                st.divider()
                with st.expander("🔄 ¿Ya pagaste? Reporta tu referencia"):
                    plan_pagado = st.selectbox("Plan Adquirido", ["PLATINUM", "DIAMANTE"])
                    ref_pago = st.text_input("Número de Referencia")
                    if st.button("ENVIAR REPORTE"):
                        if ref_pago:
                            # Notificación rápida vía WhatsApp para que tú solo verifiques y cambies el plan en Supabase
                            msj_admin = f"🚨 *PAGO RECIBIDO D'UNIG LUXURY*\n🏪 *Tienda:* {perf['nombre_comercio']}\n💎 *Plan:* {plan_pagado}\n🎫 *Ref:* {ref_pago}"
                            url_admin = f"https://wa.me/584XXXXXXXXX?text={urllib.parse.quote(msj_admin)}" # Pon tu número aquí
                            st.success("Reporte enviado. Tu plan se activará tras la verificación.")
                            st.link_button("CONFIRMAR POR WHATSAPP", url_admin)
