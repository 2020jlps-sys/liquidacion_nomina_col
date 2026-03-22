import pandas as pd

def clean_data(horas_file='HExPFMar.xlsx', clasif_file='EmplClasif.xlsx'):
    print("Leyendo archivos...")
    # Leer archivos
    df_horas = pd.read_excel(horas_file)
    # Use sheet_name='Empleados' for classification columns
    df_clasif = pd.read_excel(clasif_file, sheet_name='Empleados')

    print("Columnas de df_horas:", df_horas.columns.tolist())
    print("Columnas de df_clasif:", df_clasif.columns.tolist())

    # Left Join por la columna 'Empleado'
    df_final = pd.merge(df_horas, df_clasif, on='Empleado', how='left')

    # Convertir 'Entrada' y 'Salida' a datetime
    df_final['Entrada'] = pd.to_datetime(df_final['Entrada'])
    df_final['Salida'] = pd.to_datetime(df_final['Salida'])

    # Encontrar la columna de clasificación (usualmente 'Clasificación' o similar)
    clasif_col = [col for col in df_final.columns if 'Clasificaci' in col]
    if clasif_col:
        # Llenar nulos
        df_final[clasif_col[0]] = df_final[clasif_col[0]].fillna('Sin Clasificar')
        # Estandarizar nombre de columna para time_logic.py
        df_final.rename(columns={clasif_col[0]: 'Clasificacion'}, inplace=True)
    else:
        print("Advertencia: No se encontró la columna de clasificación.")

    print("\n[INFO DEL DATAFRAME]")
    print(df_final.info())
    print("\n[PRIMERAS FILAS]")
    print(df_final.head())
    
    return df_final

if __name__ == '__main__':
    clean_data()
