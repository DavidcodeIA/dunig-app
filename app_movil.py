import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px # Para los gráficos

# Configuración profesional
st.set_page_config(page_title="D'UNIG PRO", page_icon="📈", layout="centered")

# --- SISTEMA DE SEGURIDAD SIMPLE ---
def check_password():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.title("🔐 Acceso D'UNIG")
        clave = st.text_input("Introduce tu clave de acceso", type="password")
        if st.button("Entrar"):
            if clave == "admin123": # <--- CAMBIA TU CLAVE AQUÍ
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
        return False
    return True

if check_password():
    # --- INTERFAZ PRINCIPAL ---
    st.title("🚀 D'UNIG Business Pro")
    st.sidebar.button("Cerrar Sesión")
    
    archivo = "ventas_d_unig.xlsx"

    # Pestañas para organizar la app
    tab1, tab2, tab3 = st.tabs(["📝 Registrar", "📊 Reportes", "📂 Historial"])

    with tab1:
        with st.form("venta_pro"):
            st.write("### Nueva Venta")
            col1, col2 = st.columns(2)
            with col1:
                cliente = st.text_input("Cliente")
                producto = st.selectbox("Categoría", ["Servicio", "Producto", "Asesoría", "Otro"])
            with col2:
                cant = st.number_input("Cantidad", min_value=1)
                precio = st.number_input("Precio Unitario $", min_value=0.0)
            
            submit = st.form_submit_button("Guardar Registro")

        if submit:
            total = cant * precio
            nueva_fila = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Cliente": cliente, "Categoría": producto, 
                "Cantidad": cant, "Total $": total
            }])
            
            if os.path.exists(archivo):
                df = pd.concat([pd.read_excel(archivo), nueva_fila], ignore_index=True)
            else:
                df = nueva_fila
            df.to_excel(archivo, index=False)
            st.success(f"✅ ¡Venta de ${total} registrada exitosamente!")

    with tab2:
        st.write("### Análisis de Ingresos")
        if os.path.exists(archivo):
            df_analisis = pd.read_excel(archivo)
            ingreso_total = df_analisis["Total $"].sum()
            
            # Métrica destacada
            st.metric("Ingresos Totales", f"${ingreso_total:,.2f}")
            
            # Gráfico de barras por cliente o categoría
            fig = px.bar(df_analisis, x="Fecha", y="Total $", color="Categoría", title="Ventas por Día")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aún no hay datos para mostrar gráficos.")

    with tab3:
        st.write("### Base de Datos")
        if os.path.exists(archivo):
            df_historial = pd.read_excel(archivo)
            st.dataframe(df_historial, use_container_width=True)
            
            # Botón para descargar el Excel
            with open(archivo, "rb") as f:
                st.download_button("📥 Descargar Excel para Contador", f, file_name=archivo)
