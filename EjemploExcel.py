import pandas as pd
import streamlit as st
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="DASHBOARD PARA MRO", layout="wide")
st.title("📊 Dashboard de ejemplo de idea")

st.text("Este es un ejemplo de dashboard interactivo para visualizar datos de ventas. Puedes aplicar filtros para explorar diferentes aspectos de los datos.")
st.text("Los datos se cargan desde un archivo Excel y se visualizan utilizando gráficos interactivos.")
st.text("Los filtros se aplican en la barra lateral y los gráficos se actualizan dinámicamente según los filtros seleccionados.")
st.text("La idea es mostrar un ejemplo de dashboard para poder adaptarlo a las necesidades de mro warehouse.")

# Cargar datos
df = pd.read_excel("1000-Registros-de-ventas.xlsx", engine="openpyxl")

# Crear columna 'Ingresos' si no existe
if "Ingresos" not in df.columns and "Importe venta total" in df.columns:
    df["Ingresos"] = df["Importe venta total"]

# Convertir columna de fecha si existe
if "Fecha pedido" in df.columns:
    df["Fecha pedido"] = pd.to_datetime(df["Fecha pedido"], errors='coerce')

# Inicializar filtros
for key in ["zona", "tipo", "canal", "pais"]:
    if key not in st.session_state:
        st.session_state[key] = []

# Botón para resetear filtros
if st.sidebar.button("🔄 Resetear Filtros"):
    st.session_state.zona = []
    st.session_state.tipo = []
    st.session_state.canal = []
    st.session_state.pais = []

# Filtros en la barra lateral
st.sidebar.header("Filtros")
zonas = st.sidebar.multiselect("Zona", options=df['Zona'].dropna().unique(), key="zona")
tipos = st.sidebar.multiselect("Tipo de producto", options=df['Tipo de producto'].dropna().unique(), key="tipo")
canales = st.sidebar.multiselect("Canal de venta", options=df['Canal de venta'].dropna().unique(), key="canal")
paises = st.sidebar.multiselect("País", options=df['País'].dropna().unique(), key="pais")

# Filtro por rango de fechas
if "Fecha pedido" in df.columns:
    fecha_min = df["Fecha pedido"].min()
    fecha_max = df["Fecha pedido"].max()
    rango_fechas = st.sidebar.date_input("Rango de fechas", [fecha_min, fecha_max])
else:
    rango_fechas = None

# Aplicar filtros
df_filtrado = df.copy()
if zonas:
    df_filtrado = df_filtrado[df_filtrado['Zona'].isin(zonas)]
if tipos:
    df_filtrado = df_filtrado[df_filtrado['Tipo de producto'].isin(tipos)]
if canales:
    df_filtrado = df_filtrado[df_filtrado['Canal de venta'].isin(canales)]
if paises:
    df_filtrado = df_filtrado[df_filtrado['País'].isin(paises)]
if rango_fechas and "Fecha pedido" in df_filtrado.columns:
    df_filtrado = df_filtrado[
        (df_filtrado["Fecha pedido"] >= pd.to_datetime(rango_fechas[0])) &
        (df_filtrado["Fecha pedido"] <= pd.to_datetime(rango_fechas[1]))
    ]

# KPIs
st.markdown("### 📌 Indicadores Clave")
col_kpi1, col_kpi2 = st.columns(2)
col_kpi1.metric("💰 Total Ingresos", f"${df_filtrado['Ingresos'].sum():,.2f}")
if "Unidades" in df_filtrado.columns:
    col_kpi2.metric("📦 Total Unidades", f"{df_filtrado['Unidades'].sum():,}")

# Gráficos
fig_zona = px.bar(df_filtrado.groupby('Zona', as_index=False)['Ingresos'].sum(),
                  x='Zona', y='Ingresos', title='Ventas por Zona')

fig_tipo = px.pie(df_filtrado, names='Tipo de producto', values='Ingresos',
                  title='Ventas por Tipo de Producto')

fig_canal = px.bar(df_filtrado.groupby('Canal de venta', as_index=False)['Ingresos'].sum(),
                   x='Canal de venta', y='Ingresos', title='Ventas por Canal de Venta')

top_paises = df_filtrado.groupby('País', as_index=False)['Ingresos'].sum().nlargest(10, 'Ingresos')
fig_paises = px.bar(top_paises, x='País', y='Ingresos', title='Top 10 Países por Ventas')

# Mostrar gráficos
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_zona, use_container_width=True)
with col2:
    st.plotly_chart(fig_tipo, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig_canal, use_container_width=True)
with col4:
    st.plotly_chart(fig_paises, use_container_width=True)

# Gráfico de evolución temporal
if "Fecha pedido" in df_filtrado.columns:
    df_tiempo = df_filtrado.groupby("Fecha pedido")["Ingresos"].sum().reset_index()
    fig_tiempo = px.line(df_tiempo, x="Fecha pedido", y="Ingresos", title="Evolución de Ventas en el Tiempo")
    st.plotly_chart(fig_tiempo, use_container_width=True)

# Botón para descargar datos filtrados
st.download_button("📥 Descargar datos filtrados", df_filtrado.to_csv(index=False), "datos_filtrados.csv", "text/csv")
