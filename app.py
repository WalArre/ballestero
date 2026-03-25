import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Panel de Inteligencia Criminal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PERSONALIZADOS (CSS) ---
# Le da un aspecto más moderno, estilo tarjeta, al dashboard
st.markdown("""
    <style>
    .st-emotion-cache-1wivap2 { padding: 1rem 2rem; }
    .profile-card {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #005A9C;
        margin-bottom: 20px;
    }
    .section-title { color: #4DA8DA; font-weight: 600; margin-bottom: 10px; }
    .data-label { font-weight: bold; color: #A0A0A0; }
    .data-value { color: #FFFFFF; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        # Se asume que el CSV está en la misma carpeta que app.py
        df = pd.read_csv("investigados.csv", dtype=str)
        # Convertir coordenadas a float, manejando errores
        df['Latitud'] = pd.to_numeric(df['Latitud'], errors='coerce')
        df['Longitud'] = pd.to_numeric(df['Longitud'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("⚠️ Archivo 'investigados.csv' no encontrado. Por favor, asegúrate de que esté en el mismo directorio.")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2619/2619073.png", width=80)
st.sidebar.title("Búsqueda de Objetivos")
st.sidebar.markdown("---")

# Filtro principal
nombres_lista = df['Nombre'].dropna().unique().tolist()
objetivo_seleccionado = st.sidebar.selectbox("🔎 Seleccione Investigado:", [""] + nombres_lista)

st.sidebar.markdown("---")
st.sidebar.info(f"Total de registros en base: **{len(df)}**")

# --- PANEL PRINCIPAL ---
if objetivo_seleccionado:
    # Filtrar datos del sujeto
    sujeto = df[df['Nombre'] == objetivo_seleccionado].iloc[0]
    
    # Encabezado del Perfil
    st.markdown(f"## 🎯 Perfil de Objetivo: `{sujeto['Nombre'].upper()}`")
    st.divider()

    # Layout en 2 columnas principales (Datos / Mapa)
    col_datos, col_mapa = st.columns([1.2, 1])

    with col_datos:
        # Tarjeta de Identificación Básica
        st.markdown('<div class="section-title">IDENTIFICACIÓN BÁSICA</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("DNI", sujeto.get('DNI', 'S/D'))
        c2.metric("Nacionalidad", sujeto.get('Nacionalidad', 'S/D'))
        
        # Tarjeta de Datos de Contacto y Logística
        st.markdown('<div class="section-title" style="margin-top: 20px;">LOGÍSTICA Y CONTACTO</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"<span class='data-label'>📍 Dirección Registrada:</span> <span class='data-value'>{sujeto.get('Direccion', 'S/D')}</span>", unsafe_allow_html=True)
            st.markdown(f"<span class='data-label'>📱 Teléfonos:</span> <span class='data-value'>{sujeto.get('Telefonos', 'S/D')}</span>", unsafe_allow_html=True)
            st.markdown(f"<span class='data-label'>🚗 Vehículos:</span> <span class='data-value'>{sujeto.get('Vehiculos', 'S/D')}</span>", unsafe_allow_html=True)

        # Tarjeta de Redes y Vínculos
        st.markdown('<div class="section-title" style="margin-top: 20px;">INTELIGENCIA SOCIAL</div>', unsafe_allow_html=True)
        with st.expander("Ver Redes Sociales y Vínculos", expanded=True):
            st.markdown(f"**🌐 Redes Sociales:**\n{sujeto.get('Redes', 'S/D')}")
            st.markdown(f"**🔗 Vínculos Detectados:**\n{sujeto.get('Vinculos', 'S/D')}")

    with col_mapa:
        st.markdown('<div class="section-title">GEOLOCALIZACIÓN</div>', unsafe_allow_html=True)
        
        lat = sujeto.get('Latitud')
        lon = sujeto.get('Longitud')
        desc_fisica = sujeto.get('Descripcion_Fisica', 'Sin descripción física del lugar.')

        # Manejo de errores para coordenadas
        if pd.notna(lat) and pd.notna(lon):
            # Crear mapa interactivo con Folium
            m = folium.Map(location=[lat, lon], zoom_start=16, tiles="CartoDB dark_matter")
            
            # Crear el popup con estilo
            popup_html = f"""
            <div style="font-family: sans-serif; width: 200px;">
                <b>Objetivo:</b> {sujeto['Nombre']}<br>
                <b>Dirección:</b> {sujeto.get('Direccion', 'S/D')}<br>
                <hr style="margin: 5px 0;">
                <b>Ref. Física:</b> {desc_fisica}
            </div>
            """
            folium.Marker(
                [lat, lon],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip="Clic para ver detalles del domicilio",
                icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
            ).add_to(m)

            # Mostrar mapa en Streamlit
            st_folium(m, width=500, height=450, returned_objects=[])
        else:
            # Estado vacío si no hay coordenadas válidas
            st.warning("⚠️ No se registran coordenadas válidas (Latitud/Longitud) para este objetivo.")
            st.image("https://images.unsplash.com/photo-1524661135-423995f22d0b?ixlib=rb-4.0.3&auto=format&fit=crop&w=500&q=60", caption="Geolocalización no disponible", use_column_width=True)

else:
    # Pantalla de inicio cuando no hay nadie seleccionado
    st.info("👈 Utilice el panel lateral para seleccionar un objetivo de la base de datos.")
    st.markdown("### Resumen Rápido de la Base de Datos")
    st.dataframe(df[['Nombre', 'DNI', 'Nacionalidad', 'Direccion']].head(10), use_container_width=True)
