import os
import glob
import json
import pandas as pd

# 1. Definir la ruta de la carpeta donde están todos los archivos
carpeta_datos = './dataset_fifa' 

# 2. Cargar el dataset histórico original
ruta_csv = os.path.join(carpeta_datos, 'data_historica.csv')
print(f"Cargando datos históricos desde: {ruta_csv}")
df_historico = pd.read_csv(ruta_csv)

lista_nuevos_dfs = []

# 3. Buscar todos los archivos .json en la carpeta
archivos_json = glob.glob(os.path.join(carpeta_datos, '*.json'))
print(f"Se encontraron {len(archivos_json)} archivos JSON para procesar.\n")

# 4. Procesar cada archivo JSON iterativamente
for archivo in archivos_json:
    # Extraer el nombre del archivo sin la extensión
    nombre_base = os.path.basename(archivo)
    fecha_archivo = os.path.splitext(nombre_base)[0]
    
    # Cambiar el separador de '-' a '/' para que coincida con los datos (DD/MM/AAAA)
    fecha_ranking_formateada = fecha_archivo.replace('-', '/')
    
    # Abrir y leer el JSON
    with open(archivo, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    filas = []
    for equipo in data.get('Results', []):
        fila = {
            'rank': equipo.get('Rank'),
            'country_full': equipo['TeamName'][0]['Description'] if equipo.get('TeamName') else None,
            'country_abrv': equipo.get('IdCountry'),
            'total_points': equipo.get('TotalPoints'),
            'previous_points': equipo.get('PrevPoints'),
            'rank_change': equipo.get('RankingMovement'),
            'confederation': equipo.get('ConfederationName'),
            'rank_date': fecha_ranking_formateada # Se asigna el formato con '/'
        }
        filas.append(fila)
        
    if filas:
        df_temp = pd.DataFrame(filas)
        lista_nuevos_dfs.append(df_temp)
        print(f"✔ Procesado: {nombre_base} ({len(df_temp)} registros extraídos)")

# 5. Unir y consolidar toda la información
if lista_nuevos_dfs:
    # Unir todos los DataFrames de los JSON en uno solo
    df_nuevos = pd.concat(lista_nuevos_dfs, ignore_index=True)
    
    # Redondear los puntos a 2 decimales
    df_nuevos['total_points'] = df_nuevos['total_points'].round(2)
    df_nuevos['previous_points'] = df_nuevos['previous_points'].round(2)
    
    # Concatenar el histórico con los nuevos datos
    df_final = pd.concat([df_historico, df_nuevos], ignore_index=True)
    
    # ==========================================
    # ESTANDARIZACIÓN DE FECHAS
    # ==========================================
    # Convertimos la columna de fechas a objetos datetime para poder ordenarlas cronológicamente.
    df_final['rank_date'] = pd.to_datetime(df_final['rank_date'], dayfirst=True, format='mixed')
    
    # Ordenar por fecha (más antigua a más reciente) y luego por posición de ranking
    df_final = df_final.sort_values(by=['rank_date', 'rank'], ascending=[True, True])
    
    # Convertimos de nuevo toda la columna estrictamente al formato DD/MM/AAAA (ej. 19/01/2026)
    df_final['rank_date'] = df_final['rank_date'].dt.strftime('%d/%m/%Y')
    
    # 6. Exportar el dataset maestro actualizado
    ruta_salida = os.path.join(carpeta_datos, 'fifa_ranking_historico.csv')
    df_final.to_csv(ruta_salida, index=False)
    
    print(f"\n¡Consolidación exitosa!")
    print(f"El dataset histórico aportó {len(df_historico)} registros.")
    print(f"Se agregaron {len(df_nuevos)} registros nuevos.")
    print(f"Dataset total guardado en: {ruta_salida} con un total de {len(df_final)} filas formateadas.")
else:
    print("\nNo se pudo extraer información de los archivos JSON o la carpeta está vacía.")