import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox

# Cargar el archivo CSV y el archivo Excel
archivo_csv = 'stock-manager-export.csv'  # Cambia al nombre de tu archivo CSV
archivo_excel = 'INVENTARIO 11-02-2025.xlsx'  # Cambia al nombre de tu archivo Excel
hoja_excel = 'ExportarAExcel'  # Cambia al nombre de la hoja en el archivo Excel

# Leer los archivos en DataFrames
df_productos = pd.read_csv(archivo_csv)
df_inventario = pd.read_excel(archivo_excel, sheet_name=hoja_excel)

# Especificar la columna de referencia y las columnas de valores a mostrar
columna_referencia = 'Sku'
columna_nombre_producto = 'Product name'
columna_valor_inventario = 'Existencia'

# Imprimir los nombres de las columnas para verificar
print("Columnas en df_productos:", df_productos.columns)

# Crear un diccionario de valores de inventario basado en la columna de referencia
valores_inventario = df_inventario.set_index(columna_referencia)[columna_valor_inventario].to_dict()

# Función para buscar y mostrar el SKU en la tabla
def buscar_sku():
    sku_buscar = entry_sku.get().strip()  # Obtener el SKU ingresado y quitar espacios

    if not sku_buscar:
        messagebox.showwarning("Error", "Por favor ingresa un SKU válido.")
        return
    
    # Buscar coincidencias parciales en la columna de referencia
    productos_encontrados = df_productos[df_productos[columna_referencia].str.contains(sku_buscar, case=False, na=False)]
    
    if not productos_encontrados.empty:
        # Limpiar la tabla antes de mostrar el nuevo resultado
        for item in tree.get_children():
            tree.delete(item)
        
        # Insertar los datos en la tabla
        for _, row in productos_encontrados.iterrows():
            sku = row[columna_referencia]
            nombre_producto = row[columna_nombre_producto]
            stock_inventario = valores_inventario.get(sku, "0.0")
            tree.insert('', 'end', values=(sku, nombre_producto, stock_inventario))
    else:
        messagebox.showwarning("SKU no encontrado", f"No se encontraron productos con el SKU que contiene '{sku_buscar}'.")

# Función para limpiar la entrada y la tabla
def limpiar_busqueda():
    entry_sku.delete(0, tk.END)
    for item in tree.get_children():
        tree.delete(item)

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Consultar Referencia")
ventana.geometry("600x400")

# Crear y ubicar widgets
label_titulo = tk.Label(ventana, text="Sistema de Consulta de Productos", font=("Roboto", 16, "bold"))
label_titulo.pack(pady=10)

label_sku = tk.Label(ventana, text="Ingrese la Referencia:")
label_sku.pack(pady=5)

entry_sku = tk.Entry(ventana)
entry_sku.pack(pady=5)

btn_buscar = tk.Button(ventana, text="Buscar", command=buscar_sku, bg="Blue", fg="white")
btn_buscar.pack(pady=10)

btn_limpiar = tk.Button(ventana, text="Limpiar búsqueda", command=limpiar_busqueda)
btn_limpiar.pack(pady=5)

# Crear tabla (Treeview) para mostrar los resultados
columns = ('SKU', 'Nombre del Producto', 'Stock en Inventario')
tree = ttk.Treeview(ventana, columns=columns, show='headings')

# Definir el ancho de cada columna
tree.column('SKU', width=100)  # Ajusta el ancho según sea necesario
tree.column('Nombre del Producto', width=250)  # Ajusta el ancho según sea necesario
tree.column('Stock en Inventario', width=150)  # Ajusta el ancho según sea necesario

# Definir los encabezados de las columnas
tree.heading('SKU', text='SKU')
tree.heading('Nombre del Producto', text='Nombre del Producto')
tree.heading('Stock en Inventario', text='Stock en Inventario')

tree.pack(pady=20)

# Iniciar el bucle de la interfaz
ventana.mainloop()
