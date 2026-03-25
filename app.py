import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Criminal Intel Dashboard", page_icon="🛡️", layout="wide")

# 2. SISTEMA DE ACCESO (PASSWORD)
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔐 Acceso Restringido - Personal Autorizado</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pwd = st.text_input("Ingrese Credencial de Acceso:", type="password")
            if st.button("Ingresar"):
                if pwd == "Dicco1272":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("🚫 Clave Incorrecta")
        return False
    return True

# 3. LÓGICA PRINCIPAL
if check_password():
    # Estilos CSS para el look "Intelligence"
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #4DA8DA; }
        .stExpander { border: 1px solid #262730; }
        </style>
    """, unsafe_allow_html=True)

    # Carga de datos
    @st.cache_data
    def load_data():
        try:
            data = pd.read_csv("investigados.csv", dtype=str)
            data['Latitud'] = pd.to_numeric(data['Latitud'], errors='coerce')
            data['Longitud'] = pd.to_numeric(data['Longitud'], errors='coerce')
            return data
        except:
            return pd.DataFrame()

    df = load_data()

    if df.empty:
        st.warning("⚠️ El archivo 'investigados.csv' no existe o está vacío.")
    else:
        # SIDEBAR
        st.sidebar.title("🔍 Filtros de Búsqueda")
        lista_nombres = sorted(df['Nombre'].unique())
        seleccion = st.sidebar.selectbox("Seleccione el Objetivo:", ["--- SELECCIONAR ---"] + lista_nombres)

        if seleccion != "--- SELECCIONAR ---":
            target = df[df['Nombre'] == seleccion].iloc[0]

            # TITULO Y FICHA
            st.title(f"🎯 Objetivo: {seleccion}")
            st.divider()

            col_info, col_map = st.columns([1, 1.2])

            with col_info:
                st.subheader("📋 Ficha del Investigado")
                c1, c2 = st.columns(2)
                c1.metric("DNI", target.get('DNI', 'S/D'))
                c2.metric("Nacionalidad", target.get('Nacionalidad', 'S/D'))

                with st.expander("📍 Ubicación y Contacto", expanded=True):
                    st.write(f"**Dirección:** {target.get('Direccion', 'S/D')}")
                    st.write(f"**Teléfonos:** {target.get('Telefonos', 'S/D')}")
                
                with st.expander("🔗 Vínculos y Logística", expanded=True):
                    st.write(f"**Vínculos:** {target.get('Vinculos', 'S/D')}")
                    st.write(f"**Vehículos:** {target.get('Vehiculos', 'S/D')}")
                    st.write(f"**Redes Sociales:** {target.get('Redes', 'S/D')}")

            with col_map:
                st.subheader("🗺️ Geolocalización")
                lat, lon = target['Latitud'], target['Longitud']
                
                if pd.notna(lat) and pd.notna(lon):
                    m = folium.Map(location=[lat, lon], zoom_start=16, tiles="CartoDB dark_matter")
                    folium.Marker(
                        [lat, lon],
                        popup=f"<b>Domicilio:</b> {target.get('Descripcion_Fisica', 'S/D')}",
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(m)
                    st_folium(m, width="100%", height=400)
                    st.caption(f"Referencia Física: {target.get('Descripcion_Fisica', 'S/D')}")
                else:
                    st.warning("📍 No hay coordenadas cargadas para este objetivo.")
        else:
            st.info("Seleccione un nombre en el panel lateral para desplegar la inteligencia.")
