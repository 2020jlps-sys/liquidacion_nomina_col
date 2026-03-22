import streamlit as st
import pandas as pd
from io import BytesIO

# Configure wide layout
st.set_page_config(layout="wide", page_title="Liquidador de Horas Extras - Panna Food")

# Title
st.title("Liquidador de Horas Extras y Recargos - Panna Food")

@st.cache_data
def load_data():
    # Load dataset with semicolon separator
    df = pd.read_csv("resultados_nomina.csv", sep=";")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error cargando el archivo resultados_nomina.csv: {e}")
    st.stop()

# Sidebar for filters
st.sidebar.header("Filtros de Búsqueda")

empleados = ["Todos"] + sorted(list(df['Empleado'].dropna().unique()))
clasificaciones = ["Todas"] + sorted(list(df['Clasificacion'].dropna().unique()))

selected_empleado = st.sidebar.selectbox("Buscar por Empleado", empleados)
selected_clasificacion = st.sidebar.selectbox("Buscar por Clasificación", clasificaciones)

# Apply filters
filtered_df = df.copy()
if selected_empleado != "Todos":
    filtered_df = filtered_df[filtered_df['Empleado'] == selected_empleado]
if selected_clasificacion != "Todas":
    filtered_df = filtered_df[filtered_df['Clasificacion'] == selected_clasificacion]

# Metrics
st.subheader("Resumen de Horas")

horas_cols = ['HDO', 'HNO', 'HEDO', 'HENO', 'HDDF', 'HNDF', 'HEDDF', 'HENDF']
metric_cols = st.columns(len(horas_cols))

for i, col in enumerate(horas_cols):
    if col in filtered_df.columns:
        total = filtered_df[col].sum()
    else:
        total = 0.0
    metric_cols[i].metric(label=col, value=f"{total:.2f}")

# Data Table
st.subheader("Tabla de Registros")

# Round all hour columns to 2 decimal places for better readability
for col in horas_cols:
    if col in filtered_df.columns:
        filtered_df[col] = filtered_df[col].round(2)

st.dataframe(filtered_df, use_container_width=True)

# Generate Excel functionality
def convert_df_to_excel(df_to_export):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_to_export.to_excel(writer, index=False, sheet_name='Nomina')
    return output.getvalue()

st.sidebar.markdown("---")
st.sidebar.subheader("Descargas")

try:
    excel_data = convert_df_to_excel(filtered_df)
    st.sidebar.download_button(
        label="📥 Descargar Datos (Excel)",
        data=excel_data,
        file_name='reporte_nomina.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
except Exception as e:
    st.sidebar.error(f"Error al generar Excel. Por favor revisa las dependencias: {e}")
