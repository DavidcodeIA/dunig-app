import streamlit as st
from supabase import create_client, Client
import urllib.parse
import random

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="D'UNIG LUXURY", layout="centered", initial_sidebar_state="collapsed")

@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

PLANES = {"BRONCE": 5, "PLATINUM": 15, "DIAMANTE": 50}

if 'view' not in st.session_state: st.session_state.view = 'mall'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_email' not in st.session_state: st.session_state.user_email = None

def ir_a(pagina):
    st.session_state.view = pagina
    st.rerun()

# ==========================================
# 2. ESTÉTICA LUXURY (CSS PARA FOTO REDONDA)
# ==========================================
st.markdown("""
    <style>
    .main { background: radial-gradient(circle, #1a1a1a 0%, #000000 100%); color: #ffffff; }
    .luxury-card {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 20px; padding: 15px; text-align: center; margin-bottom: 20px;
    }
    /* Estilo para la foto redonda */
    .img-redonda {
        width: 120px; height: 120px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #D4AF37;
        margin: 0 auto 10px auto;
        display: block;
    }
    .price-bubble {
        position: absolute; top: 20px; right: 20px;
        background: rgba(0, 0, 0, 0.9); color: #39FF14; 
        padding: 8px 20px; border-radius: 50px; font-weight: 900; border: 2px solid #39FF14;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. CUERPO DE LA APP
# ==========================================
es_admin = st.query_params.get("admin") == "true"

if not es_admin:
    # --- VISTA CLIENTE (MALL) ---
    if st.session_state.view == 'mall':
        st.markdown("<h1 style='text-align:center; color:#D4AF37;'>🏙️ D'UNIG LUXURY MALL</h1>", unsafe_allow_html=True)
        res = supabase.table("perfiles_comercio").select("*").execute()
        
        # Grid de 2 filas (Streamlit maneja las columnas, las filas se crean solas al iterar)
        cols = st.columns(2)
        for idx, t in enumerate(res.data):
            with cols[idx % 2]:
                st.markdown("<div class='luxury-card'>", unsafe_allow_html=True)
                
                # Mostrar foto redonda
                if t.get('portada_url'):
                    st.markdown(f'<img src="{t["portada_url"]}" class="img-redonda">', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="img-redonda" style="background:#333; line-height:120px;">✨</div>', unsafe_allow_html=True)
                
                st.markdown(f"<h4 style='color:#D4AF37;'>{t['nombre_comercio'].upper()}</h4>", unsafe_allow_html=True)
                if st.button("VISITAR", key=f"mall_{t['id']}", use_container_width=True):
                    st.session_state.tienda_actual = t
                    ir_a('tienda')
                st.markdown("</div>", unsafe_allow_html=True)

    elif st.session_state.view == 'tienda':
        t = st.session_state.tienda_actual
        if st.button("⬅️ VOLVER"): ir_a('mall')
        st.markdown(f"<h1 style='text-align:center; color:#D4AF37;'>{t['nombre_comercio']}</h1>", unsafe_allow_html=True)
        prods = supabase.table("productos").select("*").eq("comercio_relacionado", t['nombre_comercio']).execute()
        for p in prods.data:
            st.markdown(f"<div style='position: relative;'><div class='price-bubble'>${p['precio']}</div></div>", unsafe_allow_html=True)
            st.video(p['video_url'])
            st.divider()

else:
    # --- PANEL ADMIN ---
    if not st.session_state.logged_in:
        # (Login omitido por brevedad, mantén el tuyo igual)
        pass 
    else:
        res = supabase.table("perfiles_comercio").select("*").eq("email_propietario", st.session_state.user_email).execute()
        if res.data:
            perf = res.data[0]
            t1, t2, t3, t4, t5, t6 = st.tabs(["➕ AGREGAR", "📦 GESTIÓN", "💳 COBROS", "🖼️ PORTADA", "💎 PLAN", "✨ REGISTRO"])
            
            with t6: # REGISTRO CON CARGA DE PORTADA
                st.markdown("### 🆕 Registrar Nuevo Propietario")
                with st.form("reg_nuevo_full", clear_on_submit=True):
                    r_nom = st.text_input("Nombre de la Tienda")
                    r_mail = st.text_input("Email Propietario")
                    r_tel = st.text_input("WhatsApp")
                    r_img = st.file_uploader("Foto de Portada/Logo", type=['jpg', 'png', 'jpeg'])
                    if st.form_submit_button("💎 REGISTRAR TIENDA COMPLETA"):
                        if r_nom and r_mail and r_tel:
                            url_final = None
                            if r_img:
                                # Subir imagen
                                f_name = f"portadas/reg_{random.randint(1000,9999)}.jpg"
                                supabase.storage.from_("fotos_productos").upload(path=f_name, file=r_img.getvalue(), file_options={"upsert": True})
                                url_final = supabase.storage.from_("fotos_productos").get_public_url(f_name)
                            
                            # Insertar en base de datos
                            supabase.table("perfiles_comercio").insert({
                                "nombre_comercio": r_nom,
                                "email_propietario": r_mail.lower(),
                                "whatsapp": r_tel,
                                "portada_url": url_final,
                                "plan": "BRONCE"
                            }).execute()
                            st.success(f"¡Tienda {r_nom} registrada!")
                        else:
                            st.error("Campos obligatorios faltantes")

            with t4: # ACTUALIZAR PORTADA EXISTENTE
                st.subheader("🖼️ Cambiar mi Imagen")
                new_p = st.file_uploader("Nueva foto", type=['jpg', 'png'], key="p_update")
                if st.button("GUARDAR CAMBIOS"):
                    if new_p:
                        path_p = f"portadas/perfil_{perf['id']}.jpg"
                        supabase.storage.from_("fotos_productos").upload(path=path_p, file=new_p.getvalue(), file_options={"upsert": True})
                        url_p = supabase.storage.from_("fotos_productos").get_public_url(path_p)
                        supabase.table("perfiles_comercio").update({"portada_url": url_p}).eq("id", perf['id']).execute()
                        st.rerun()