import pandas as pd
from datetime import datetime

# Cargar los archivos de Excel
archivo_excel_productos = 'EXISTENCIA CRM.xlsx'  # Cambia al nombre de tu archivo Excel de productos
archivo_excel_inventario = 'INVENTARIO 22-04-2025.xlsx'  # Cambia al nombre de tu archivo Excel de inventario
hoja_productos = 'Hoja1'  # Cambia al nombre de la hoja en el archivo de productos
hoja_inventario = 'ExportarAExcel'  # Cambia al nombre de la hoja en el archivo de inventario

# Leer los archivos en DataFrames
df_productos = pd.read_excel(archivo_excel_productos, sheet_name=hoja_productos)
df_inventario = pd.read_excel(archivo_excel_inventario, sheet_name=hoja_inventario)

# Especificar la columna de referencia y las columnas de valores a actualizar
columna_referencia = 'Sku'
columna_valor_producto = 'Existencia'  # Cambia al nombre de la columna en productos que deseas actualizar
columna_valor_inventario = 'Existencia'  # Cambia al nombre de la columna en inventario

# Crear un diccionario de valores de inventario basado en la columna de referencia
valores_inventario = df_inventario.set_index(columna_referencia)[columna_valor_inventario].to_dict()

# Actualizar los valores en la hoja de productos
df_productos[columna_valor_producto] = df_productos[columna_referencia].map(valores_inventario)

# Generar el nombre del archivo con la fecha actual
fecha_actual = datetime.now().strftime('%Y-%m-%d')
nombre_archivo_salida = f'INVENTARIO_{fecha_actual}.xlsx'

# Guardar el DataFrame actualizado en un nuevo archivo Excel
df_productos.to_excel(nombre_archivo_salida, index=False, sheet_name="Inventario Actualizado")

print(f'Archivo guardado como {nombre_archivo_salida}')
