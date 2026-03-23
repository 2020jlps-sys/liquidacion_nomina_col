# Liquidador de Nómina Colombia - Panna Food

Bienvenido al repositorio del **Liquidador de Nómina Colombia** para Panna Food. Esta aplicación resuelve el complejo problema de negocio de calcular automáticamente las horas extras, recargos nocturnos, dominicales y festivos de manera precisa y alineada con la legislación laboral colombiana. Elimina horas de trabajo manual, reduce el margen de error humano y agiliza los procesos del departamento de Recursos Humanos.

## Arquitectura del Sistema (El Trío Dinámico)

La aplicación está diseñada bajo una arquitectura modular de tres componentes principales que aseguran un flujo de información limpio, eficiente y escalable:

### 1. Data Cleaner (`data_cleaner.py`)
Es el encargado de la **estandarización y limpieza de datos crudos**. 
- Recibe los archivos de Excel con registros de entradas/salidas y la base de datos de empleados.
- Ejecuta cruces de información (Left Join) para asignar a cada empleado su clasificación correspondiente.
- Convierte y estandariza las fechas y horas al formato adecuado (`datetime`) e imputa valores nulos, generando un set de datos íntegro y preparado para un rápido procesamiento.

### 2. Time Logic (`time_logic.py`)
Es el **núcleo matemático y legal** del sistema. Recibe los datos limpios y aplica las complejas normativas del código laboral colombiano de manera estricta:
- **Jornadas Máximas:** Determina el límite de horas ordinarias y el punto donde inician las extras, basándose en el día de la semana y el perfil del empleado (ej. Sup, Aux, Enc).
- **Regla del Almuerzo:** Realiza el descuento automático de tiempo de descanso de manera equitativa e inteligente, priorizando descontar el tiempo base si el turno cruza el umbral del mediodía.
- **Ley Emiliani (Dominicales y Festivos):** Integración dinámica con el calendario colombiano (usando la librería `holidays`) para identificar automáticamente días festivos y domingos, aplicando los recargos de ley de forma automática.
- **Cortes y Distribución:** Segmenta los turnos para clasificar de manera microscópica y precisa todas las horas trabajadas en HDO, HNO, HEDO, HENO, HDDF, HNDF, HEDDF y HENDF.

### 3. Streamlit UI (`app.py`)
La **interfaz gráfica interactiva** para el usuario final, pensada para la usabilidad.
- Provee un entorno amigable en web donde el usuario interactúa con la herramienta de forma intuitiva, sin necesidad de saber programar.
- Orquesta las capas de limpieza y cálculo, conectándolas con funciones de visualización para ver métricas clave en tiempo real.
- Permite la aplicación dinámica de filtros (por empleado específico o su clasificación).

## Seguridad y Privacidad

El sistema ha sido arquitectado bajo el principio de **privacidad por diseño (Privacy by Design)**.
Aplicamos cálculos y transformaciones **estrictamente en memoria (In-Memory Processing)** dentro de la nube. 
- Los archivos Excel que contienen información confidencial (nombres de empleados, horarios y condiciones) **nunca se almacenan en servidores públicos ni bases de datos persistentes**. 
- Todo el procesamiento ocurre en tiempo de ejecución. Al cerrar la aplicación o finalizar la sesión del usuario, la información temporal desaparece de la memoria ram por completo, blindando así los datos de la corporación.

## Stack Tecnológico

El proyecto está desarrollado completamente en el lenguaje Python e implementa un ecosistema eficiente de librerías especializadas:

- **Streamlit:** Framework para el desarrollo y despliegue rápido de la interfaz gráfica y presentación analítica de los datos.
- **Pandas:** El estándar de la industria en modelado analítico para la limpieza de columnas, operaciones JOIN y segmentación de datos tabulares (DataFrames).
- **Holidays:** Dependencia vital para reconocer de forma programática las fechas exactas de las festividades variables (y fijas) de Colombia de todos los años.
- **OpenPyXL:** Motor subyacente de lectura y escritura para comunicarse orgánicamente con hojas de cálculo MS Excel reales.

## Instrucciones de Uso

Para utilizar la herramienta de liquidación desde **Streamlit Cloud**, siga el procedimiento estándar como usuario final:

1. **Subir Archivos:** Abra la barra lateral de la izquierda (Sidebar) y localice las zonas de carga. Suba primeramente el archivo de horas mensuales (`HExPFMar.xlsx`) y seguidamente su listado maestro con los perfiles (`EmplClasif.xlsx`).
2. **Revisar Dashboard Interactivo:** En tan solo unos segundos, el algoritmo ejecutará todo el recálculo mensual y mostrará el panel central de reportes. Analice el resumen de todas las horas generadas (HDO, HENO, HDDF, etc.) y descienda por los registros consolidados de empleados en la tabla principal. Aproveche los filtros si desea auditar un empleado particular.
3. **Descargar Resultados:** Cuando esté conforme con la lectura, muévase a la sección inferior de la barra lateral y presione el botón **"📥 Descargar Datos (Excel)"**. Esto generará al instante un archivo `reporte_nomina.xlsx` limpio y ordenado hacia su sistema local que podrá utilizar en su software contable actualizado.
