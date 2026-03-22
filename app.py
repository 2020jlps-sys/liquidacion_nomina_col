import streamlit as st
import pandas as pd
from io import BytesIO
from data_cleaner import clean_data
from time_logic import calculate_time_classifications

# Configure wide layout
st.set_page_config(layout="wide", page_title="Liquidador de Horas Extras - Panna Food")

# Title
st.title("Liquidador de Horas Extras y Recargos - Panna Food")

st.sidebar.header("Carga de Archivos")
horas_file = st.sidebar.file_uploader("Sube el archivo de horas (HExPFMar.xlsx)", type=['xlsx'])
clasif_file = st.sidebar.file_uploader("Sube el archivo de empleados (EmplClasif.xlsx)", type=['xlsx'])

@st.cache_data
def process_nomina_files(horas, clasif):
    # Pass uploaded files to data_cleaner
    df_clean = clean_data(horas, clasif)
    # Run business logic to calculate hours
    df_result = calculate_time_classifications(df_clean)
    return df_result

if horas_file is None or clasif_file is None:
    st.info("Por favor, sube los archivos de Excel en la barra lateral para iniciar la liquidación.")
    st.stop()

try:
    with st.spinner("Procesando datos y calculando nómina. Esto puede tomar unos segundos..."):
        df = process_nomina_files(horas_file, clasif_file)
except Exception as e:
    st.error(f"Error procesando los archivos: {e}")
    st.stop()

# Sidebar for filters
st.sidebar.markdown("---")
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
    st.sidebar.error(f"Error al generar Excel: {e}")
