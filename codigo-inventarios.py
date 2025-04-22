import pandas as pd

# Cargar el archivo CSV y el archivo Excel
archivo_csv = 'stock-manager-export.csv'  # Cambia al nombre de tu archivo CSV
archivo_excel = 'INVENTARIO 11-02-2025.xlsx'  # Cambia al nombre de tu archivo Excel
hoja_excel = 'ExportarAExcel'  # Cambia al nombre de la hoja en el archivo Excel

# Leer los archivos en DataFrames
df_productos = pd.read_csv(archivo_csv)
df_inventario = pd.read_excel(archivo_excel, sheet_name=hoja_excel)

# Especificar la columna de referencia y las columnas de valores a actualizar
columna_referencia = 'Sku'
columna_valor_producto = 'Stock'  # Cambia al nombre de la columna en productos que deseas actualizar
columna_valor_inventario = 'Existencia'  # Cambia al nombre de la columna en inventario

# Crear un diccionario de valores de inventario basado en la columna de referencia
valores_inventario = df_inventario.set_index(columna_referencia)[columna_valor_inventario].to_dict()

# Actualizar los valores en la hoja de productos
df_productos[columna_valor_producto] = df_productos[columna_referencia].map(valores_inventario)

# Guardar el DataFrame actualizado en un nuevo archivo CSV
df_productos.to_csv('productos_actualizados.csv', index=False)

# Opcional: Si prefieres guardar en un archivo Excel, usa el siguiente comando:
# df_productos.to_excel('productos_actualizados.xlsx', index=False)

#=SI.ERROR(IZQUIERDA(A2;ENCONTRAR(" ";A2)-1); A2) Formula para sacar la referencia en el archivo excel

#ANY(SELECT(MOLDES[NUMERO MOLDE], [REFERENCIA] = [_THISROW].[REFERENCIA MOLDE]))

#ANY(SELECT(REFERENCIA MOLDES[REFERENCIA], [MOLDE] = [_THISROW].[NUMERO MOLDE]))