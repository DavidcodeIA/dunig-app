import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="D'UNIG - Asistente", layout="wide", page_icon="🙏")
EXCEL_FILE = 'ventas_d_unig.xlsx'

st.title("🚀 D'UNIG: Tu Guía Espiritual y Práctica")

if os.path.exists(EXCEL_FILE):
    try:
        # Intentamos abrirlo forzando el motor 'openpyxl'
        # Usamos un bloque with para asegurar que el archivo se abra y cierre bien
        with open(EXCEL_FILE, "rb") as f:
            df = pd.read_excel(f, engine='openpyxl')
        
        if df.empty:
            st.warning("⚠️ El archivo Excel está en blanco.")
        else:
            st.success(f"✅ ¡Datos cargados! Columnas: {list(df.columns)}")
            st.dataframe(df, use_container_width=True)
            
            # Gráfico dinámico basado en lo que encuentre
            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            if num_cols:
                fig = px.bar(df, x=df.columns[0], y=num_cols[0], title="Visualización de Datos")
                st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        # Si falla, intentamos leerlo como CSV por si acaso se guardó mal
        try:
            df = pd.read_csv(EXCEL_FILE)
            st.success("✅ Detectado como formato CSV.")
            st.dataframe(df)
        except:
            st.error(f"Error técnico: {e}")
            st.info("Prueba a abrir tu Excel en la PC, dale a 'Guardar como', asegúrate de que sea '.xlsx' y súbelo de nuevo a GitHub.")
else:
    st.error(f"❌ No se encuentra el archivo '{EXCEL_FILE}'")

st.sidebar.markdown("---")
st.sidebar.info("✨ Guardar los mandamientos de Dios y su ley como la niña de los ojos.")
