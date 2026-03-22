import pandas as pd
from datetime import timedelta
import holidays
import warnings

# Suprimimos posibles warnings de pandas relacionados a asignaciones encadenadas
warnings.filterwarnings('ignore')

def calculate_time_classifications(df: pd.DataFrame) -> pd.DataFrame:
    """
    Toma un DataFrame con columnas ['Empleado', 'Entrada', 'Salida', 'Clasificacion']
    y calcula las horas HDO, HNO, HEDO, HENO, HDDF, HNDF, HEDDF, HENDF.
    """
    co_holidays = holidays.CO()
    
    # Asegurarnos de que las columnas de fechas están como datetime
    if not pd.api.types.is_datetime64_any_dtype(df['Entrada']):
        df['Entrada'] = pd.to_datetime(df['Entrada'])
    if not pd.api.types.is_datetime64_any_dtype(df['Salida']):
        df['Salida'] = pd.to_datetime(df['Salida'])
        
    cols = ['HDO', 'HNO', 'HEDO', 'HENO', 'HDDF', 'HNDF', 'HEDDF', 'HENDF']
    
    def process_row(row):
        entrada = row['Entrada']
        salida = row['Salida']
        clasificacion = str(row['Clasificacion']).strip().title()
        
        # Resultados inicializados en 0.0
        res = {c: 0.0 for c in cols}
        
        if pd.isnull(entrada) or pd.isnull(salida):
            return pd.Series(res)
            
        # 1. Jornada Máxima
        dia_semana = entrada.weekday()  # Lunes=0, Domingo=6
        
        if clasificacion == 'Sup':
            # Sup: Lun-Jue(0-3) = 7h. Vie-Dom(4-6) = 8h.
            jornada_max = 7 if dia_semana <= 3 else 8
        else:
            # Aux, Rfz, Enc: Dom-Jue(6, 0-3) = 7h. Vie-Sab(4,5) = 8h.
            if dia_semana == 4 or dia_semana == 5:
                jornada_max = 8
            else:
                jornada_max = 7
                
        # 2. Descuento almuerzo y umbral extra
        limit_time = pd.Timestamp("12:00:00").time()
        if entrada.time() <= limit_time:
            bono_almuerzo = 1
        else:
            bono_almuerzo = 0
            
        umbral_extra = entrada + pd.Timedelta(hours=(jornada_max + bono_almuerzo))
        
        # 3. Cortes
        cortes = [entrada, salida]
        if entrada < umbral_extra < salida:
            cortes.append(umbral_extra)
            
        # Generar puntos de corte de fechas/días/horas entre entrada y salida
        curr_date = entrada.date()
        end_date = salida.date()
        
        d = curr_date
        while d <= end_date:
            medianoche = pd.Timestamp(d)
            if entrada < medianoche < salida:
                cortes.append(medianoche)
                
            seis_am = pd.Timestamp(d) + pd.Timedelta(hours=6)
            if entrada < seis_am < salida:
                cortes.append(seis_am)
                
            siete_pm = pd.Timestamp(d) + pd.Timedelta(hours=19)
            if entrada < siete_pm < salida:
                cortes.append(siete_pm)
                
            d += pd.Timedelta(days=1)
            
        # Ordenar y eliminar duplicados para dejar cortes consecutivos cronológicamente
        cortes = sorted(list(set(cortes)))
        
        # 4. Iterar y clasificar Segmentos
        for i in range(len(cortes) - 1):
            start = cortes[i]
            end = cortes[i+1]
            duracion = (end - start).total_seconds() / 3600.0
            
            if duracion <= 0:
                continue
                
            # ¿Es festivo o domingo?
            es_dom_fest = (start.weekday() == 6) or (start.date() in co_holidays)
            
            # ¿Es nocturno? (Rango >= 19 o < 6)
            es_nocturno = start.hour >= 19 or start.hour < 6
            
            # ¿Es jornada extra? (Si empezó en o después del umbral extra)
            es_extra = start >= umbral_extra
            
            if es_dom_fest:
                if es_extra:
                    if es_nocturno: res['HENDF'] += duracion
                    else: res['HEDDF'] += duracion
                else:
                    if es_nocturno: res['HNDF'] += duracion
                    else: res['HDDF'] += duracion
            else:
                if es_extra:
                    if es_nocturno: res['HENO'] += duracion
                    else: res['HEDO'] += duracion
                else:
                    if es_nocturno: res['HNO'] += duracion
                    else: res['HDO'] += duracion
                    
        # 5. Descuento Almuerzo
        if bono_almuerzo > 0:
            # Descontar preferiblemente de tiempos diurnos ordinarios logeados
            if res['HDO'] >= 1:
                res['HDO'] -= 1
            elif res['HDDF'] >= 1:
                res['HDDF'] -= 1
            else:
                # Caso atípico contingencia, descontar donde se halle alguna hora ordinaria
                for p_col in ['HDO', 'HDDF', 'HNO', 'HNDF']:
                    if res[p_col] >= 1:
                        res[p_col] -= 1
                        break
                        
        # 6. Excepción 'Enc'
        if clasificacion == 'Enc':
            res['HDO'] += res['HEDO']
            res['HEDO'] = 0.0
            
            res['HNO'] += res['HENO']
            res['HENO'] = 0.0
            
            res['HDDF'] += res['HEDDF']
            res['HEDDF'] = 0.0
            
            res['HNDF'] += res['HENDF']
            res['HENDF'] = 0.0
            
        return pd.Series(res)

    # Aplicamos la función fila por fila
    df_result = df.copy()
    resultados = df_result.apply(process_row, axis=1)
    
    # Asignamos las nuevas columnas al dataframe de resultado
    for c in cols:
        df_result[c] = resultados[c]
        
    return df_result

if __name__ == '__main__':
    # Casos límite de prueba definidos en el Plan Lógico
    data = [
        {'Empleado': 'E1 - Caso A', 'Entrada': '2026-03-23 15:00:00', 'Salida': '2026-03-23 23:00:00', 'Clasificacion': 'Sup'}, # Sup Lunes, >12:00
        {'Empleado': 'E2 - Caso B', 'Entrada': '2026-03-20 08:00:00', 'Salida': '2026-03-20 18:00:00', 'Clasificacion': 'Aux'}, # Aux Viernes, <=12:00
        {'Empleado': 'E3 - Caso C', 'Entrada': '2026-03-21 20:00:00', 'Salida': '2026-03-22 05:00:00', 'Clasificacion': 'Enc'}, # Enc Sábado->Domingo Festivo
    ]
    df_test = pd.DataFrame(data)
    
    df_res = calculate_time_classifications(df_test)
    
    # Mostramos los resultados importantes
    cols_to_print = ['Empleado', 'HDO', 'HNO', 'HEDO', 'HENO', 'HNDF', 'HENDF']
    print("\n--- Resultados de los 3 Casos Límite ---")
    print(df_res[cols_to_print].to_string(index=False))
    print("------------------------------------------\n")
