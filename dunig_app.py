import streamlit as st
from supabase import create_client
import urllib.parse

# ==========================================
# 1. CONFIGURACIÓN Y CONEXIÓN
# ==========================================
st.set_page_config(
    page_title="D'UNIG LUXURY", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# [Omitido por brevedad: Conexión a Supabase]

# ==========================================
# 2. SCRIPT DE AUDIO FOCUS (JAVASCRIPT)
# ==========================================
# Este script detecta el scroll y activa el sonido del video que está en pantalla
# mientras silencia los demás, emulando el comportamiento de TikTok.
st.components.v1.html("""
<script>
    function manageAudioFocus() {
        const videos = window.parent.document.querySelectorAll('video');
        const windowHeight = window.parent.innerHeight;

        videos.forEach(video => {
            const rect = video.getBoundingClientRect();
            // Si el video está en el centro de la pantalla (activo)
            if (rect.top >= 0 && rect.bottom <= windowHeight) {
                video.muted = false; // Activa sonido
                video.play();
            } else {
                video.muted = true; // Silencia videos pasivos
            }
        });
    }

    // Activar audio al primer toque del usuario (Requisito del navegador)
    window.parent.document.addEventListener('click', () => {
        const videos = window.parent.document.querySelectorAll('video');
        videos.forEach(v => { v.muted = false; v.play(); });
        manageAudioFocus();
    }, { once: true });

    // Gestionar audio durante el scroll (Snap)
    window.parent.addEventListener('scroll', manageAudioFocus);
</script>
""", height=0)

# ==========================================
# 3. CSS DE ALTA PRECISIÓN (SIN ESPACIOS)
# ==========================================
st.markdown("""
    <style>
    .main { background-color: #000000 !important; }
    header { visibility: hidden; display: none !important; }
    footer { visibility: hidden; }
    
    /* Elimina el espacio superior de Streamlit de raíz */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0rem !important;
        margin-top: -85px !important; /* Ajuste máximo para pegar el video al borde */
        padding-bottom: 0rem !important;
        padding-left: 0rem !important;
        padding-right: 0rem !important;
        max-width: 100% !important;
    }

    [data-testid="stVerticalBlock"] {
        scroll-snap-type: y mandatory;
        overflow-y: scroll;
        height: 100vh;
        gap: 0rem !important;
    }

    .snap-section {
        scroll-snap-align: start;
        scroll-snap-stop: always;
        position: relative;
        width: 100vw;
        height: 100vh;
        background: #000;
    }

    .tiktok-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* Botón ATRÁS (Naranja Neón - Arriba a la izquierda) */
    div.stButton > button[key^="back_"] {
        position: fixed;
        top: 25px !important; 
        left: 15px !important;
        z-index: 2000 !important;
        background: rgba(0, 0, 0, 0.7) !important;
        color: #FF5F1F !important; 
        border: 2px solid #FF5F1F !important;
        border-radius: 50px !important;
        font-weight: 900 !important;
        padding: 5px 20px !important;
    }

    /* Botón COMPRAR (Dorado Luxury - Abajo) */
    div.stButton > button[key^="buy_"] {
        position: fixed;
        bottom: 0px !important;
        left: 0px !important;
        z-index: 1000 !important;
        background: linear-gradient(90deg, #8A6E2F, #D4AF37, #F9F295, #D4AF37, #8A6E2F) !important;
        color: #000 !important; 
        border-radius: 0px !important; 
        font-weight: 900 !important;
        height: 75px !important;
        width: 100% !important;
        font-size: 1.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. VISTA DE TIENDA
# ==========================================
if st.session_state.view == 'tienda':
    # Simulación de carga de productos
    for idx in range(3):
        st.markdown(f"""
            <div class="snap-section">
                <video class="tiktok-video" loop playsinline muted>
                    <source src="URL_DE_TU_VIDEO_AQUÍ" type="video/mp4">
                </video>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("⬅ ATRÁS", key=f"back_{idx}"):
            st.session_state.view = 'mall'
            st.rerun()

        if st.button(f"🛒 COMPRAR AHORA", key=f"buy_{idx}"):
            st.write("Abriendo carrito...")