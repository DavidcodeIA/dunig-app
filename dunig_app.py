# Agregar esto a tu bloque de CSS en st.markdown
st.markdown("""
    <style>
    /* El contenedor principal ahora permite el imán vertical */
    [data-testid="stVerticalBlock"] {
        scroll-snap-type: y mandatory;
        overflow-y: scroll;
        height: 100vh;
        gap: 0rem !important;
    }

    /* Cada bloque de producto se ajusta al inicio de la pantalla */
    .video-container-916 {
        scroll-snap-align: start;
        scroll-snap-stop: always;
        height: 100vh; /* Forzamos a que cada video ocupe la pantalla completa */
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    /* Movemos los botones para que floten SOBRE el video */
    .floating-controls {
        position: absolute;
        bottom: 120px;
        right: 20px;
        display: flex;
        flex-direction: column;
        gap: 15px;
        z-index: 20;
    }
    </style>
""", unsafe_allow_html=True)