import pandas as pd
from data_cleaner import clean_data
from time_logic import calculate_time_classifications

def main():
    print("Iniciando generación de nómina...")
    
    # 1. Obtener y limpiar datos
    df_clean = clean_data()
    
    if df_clean is None or df_clean.empty:
        print("Error: No se obtuvieron datos desde data_cleaner.")
        return
        
    print(f"\nDatos limpios obtenidos: {len(df_clean)} registros.")
    
    # 2. Calcular clasificaciones de horas
    print("Aplicando lógica de clasificación de tiempos por ley colombiana...")
    df_result = calculate_time_classifications(df_clean)
    
    # Mostrar resultados en consola (resumen)
    cols_to_print = ['Empleado', 'Entrada', 'Salida', 'Clasificacion', 'HDO', 'HNO', 'HEDO', 'HENO', 'HNDF', 'HENDF']
    
    print("\nMuestra de las clasificaciones calculadas:")
    print(df_result.head()[cols_to_print].to_string(index=False))
    
    # 3. Exportar resultados a CSV
    output_path = 'resultados_nomina.csv'
    # Usamos utf-8-sig para que Excel lo lea con tildes correctamente
    df_result.to_csv(output_path, index=False, encoding='utf-8-sig', sep=';')
    
    print(f"\n¡Éxito! El proceso ha finalizado.")
    print(f"El archivo final fue exportado correctamente en: {output_path}")

if __name__ == '__main__':
    main()
