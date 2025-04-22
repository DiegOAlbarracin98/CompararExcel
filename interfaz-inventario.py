import streamlit as st
import pandas as pd

# Configurar la interfaz
st.title("Actualización de Inventario")

# Subir archivos
archivo_csv = st.file_uploader("Sube el archivo CSV de productos", type=["csv"])
archivo_excel = st.file_uploader("Sube el archivo Excel de inventario", type=["xlsx"])

if archivo_csv and archivo_excel:
    try:
        hoja_excel = "ExportarAExcel"  # Cambia si el nombre de la hoja es diferente

        # Leer los archivos en DataFrames
        df_productos = pd.read_csv(archivo_csv)
        df_inventario = pd.read_excel(archivo_excel, sheet_name=hoja_excel)

        # Especificar la columna de referencia y las columnas de valores a actualizar
        columna_referencia = "Sku"
        columna_valor_producto = "Stock"
        columna_valor_inventario = "Existencia"

        # Crear un diccionario de valores de inventario basado en la columna de referencia
        valores_inventario = df_inventario.set_index(columna_referencia)[columna_valor_inventario].to_dict()

        # Actualizar los valores en la hoja de productos
        df_productos[columna_valor_producto] = df_productos[columna_referencia].map(valores_inventario)

        # Mostrar la tabla actualizada
        st.subheader("Productos Actualizados")
        st.dataframe(df_productos)

        # Agregar una barra de búsqueda por SKU
        sku_busqueda = st.text_input("Buscar producto por SKU")
        if sku_busqueda:
            resultado_busqueda = df_productos[df_productos[columna_referencia].astype(str).str.contains(sku_busqueda, case=False, na=False)]
            st.dataframe(resultado_busqueda)
        
        # Convertir el DataFrame actualizado en un archivo descargable
        csv_actualizado = df_productos.to_csv(index=False).encode("utf-8")

        st.success("Actualización completada.")

        # Botón para descargar el archivo actualizado
        st.download_button(
            label="Descargar productos_actualizados.csv",
            data=csv_actualizado,
            file_name="productos_actualizados.csv",
            mime="text/csv",
        )
    
    except Exception as e:
        st.error(f"Error en el procesamiento: {e}")
