import streamlit as st
import pandas as pd
from io import BytesIO
import re

st.set_page_config(page_title="Comparador de referencias", layout="centered")
st.title("📦 Comparador de referencias entre archivos Excel o CSV")

# Carga de archivos
archivo1 = st.file_uploader("📄 Sube el primer archivo", type=["xlsx", "csv"])
archivo2 = st.file_uploader("📄 Sube el segundo archivo", type=["xlsx", "csv"])

columna1 = st.text_input("📝 Nombre de la columna en el primer archivo (ej: 'Referencia')")
columna2 = st.text_input("📝 Nombre de la columna en el segundo archivo (ej: 'Código')")

# Opciones avanzadas
st.subheader("⚙️ Opciones de comparación")
col1, col2, col3 = st.columns(3)
with col1:
    ignorar_mayusculas = st.checkbox("Ignorar mayúsculas/minúsculas", value=True)
with col2:
    ignorar_espacios = st.checkbox("Ignorar espacios en blanco", value=True)
with col3:
    ignorar_caracteres = st.checkbox("Ignorar caracteres especiales", value=False)

caracteres_especiales = st.text_input(
    "Caracteres a ignorar (ej: '-', '.', '/', '*')",
    value="-.",
    help="Separa los caracteres sin espacios"
)

# Función para leer Excel o CSV
def leer_archivo(archivo):
    if archivo.name.endswith(".csv"):
        return pd.read_csv(archivo)
    else:
        return pd.read_excel(archivo)

# Función mejorada de limpieza de texto
def limpiar_referencia(texto, ignorar_mayusculas=True, ignorar_espacios=True, 
                       ignorar_caracteres=False, caracteres_especiales=""):
    if not isinstance(texto, str):
        return ""
    
    # Convertir a mayúsculas si se especifica
    if ignorar_mayusculas:
        texto = texto.upper()
    
    # Reemplazar caracteres especiales comunes
    texto = texto.replace("\n", " ").replace("Ω", "0").replace("ø", "0").replace("Ø", "0")
    
    # Eliminar caracteres especiales si se solicita
    if ignorar_caracteres and caracteres_especiales:
        for char in caracteres_especiales:
            texto = texto.replace(char, "")
    
    # Eliminar espacios en blanco si se solicita
    if ignorar_espacios:
        texto = re.sub(r'\s+', '', texto)
    else:
        texto = re.sub(r'\s+', ' ', texto).strip()
    
    return texto

if archivo1 and archivo2 and columna1 and columna2:
    try:
        df1 = leer_archivo(archivo1)
        df2 = leer_archivo(archivo2)

        if columna1 not in df1.columns:
            st.error(f"❌ La columna '{columna1}' no existe en el primer archivo.")
            st.info(f"Columnas disponibles: {', '.join(df1.columns)}")
        elif columna2 not in df2.columns:
            st.error(f"❌ La columna '{columna2}' no existe en el segundo archivo.")
            st.info(f"Columnas disponibles: {', '.join(df2.columns)}")
        else:
            # Convertir a string y limpiar referencias
            df1[columna1] = df1[columna1].astype(str).apply(
                lambda x: limpiar_referencia(x, ignorar_mayusculas, ignorar_espacios, 
                                             ignorar_caracteres, caracteres_especiales)
            )
            df2[columna2] = df2[columna2].astype(str).apply(
                lambda x: limpiar_referencia(x, ignorar_mayusculas, ignorar_espacios, 
                                             ignorar_caracteres, caracteres_especiales)
            )

            # Crear sets para comparación
            referencias_2 = set(df2[columna2])
            referencias_1 = set(df1[columna1])
            
            # Agregar columna de coincidencia al primer archivo
            df1["¿Está en ambos?"] = df1[columna1].apply(lambda x: "✅" if x in referencias_2 else "❌")

            st.success("✅ Comparación realizada con éxito.")
            st.subheader("📋 Resultado del primer archivo:")
            st.dataframe(df1, use_container_width=True)

            # Referencias exclusivas
            solo_en_1 = sorted(referencias_1 - referencias_2)
            solo_en_2 = sorted(referencias_2 - referencias_1)

            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander(f"🔍 Solo en archivo 1 ({len(solo_en_1)})"):
                    if solo_en_1:
                        st.write(solo_en_1)
                    else:
                        st.write("✅ Sin referencias exclusivas")

            with col2:
                with st.expander(f"🔍 Solo en archivo 2 ({len(solo_en_2)})"):
                    if solo_en_2:
                        st.write(solo_en_2)
                    else:
                        st.write("✅ Sin referencias exclusivas")

            # Estadísticas
            st.subheader("📊 Estadísticas:")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Archivo 1", len(referencias_1))
            with col2:
                st.metric("Total Archivo 2", len(referencias_2))
            with col3:
                coincidencias = len(referencias_1 & referencias_2)
                st.metric("Coincidencias", coincidencias)
            with col4:
                diferencias = len(referencias_1 ^ referencias_2)
                st.metric("Diferencias", diferencias)

            # --- Comparación adicional si existen columnas de cantidad ---
            st.subheader("📦 Comparación avanzada (si aplica):")
            
            # Crear columnas numéricas si existen
            cantidad_cols_df1 = [col for col in df1.columns if any(x in col.lower() for x in ['cantidad', 'qty', 'stock', 'unidad'])]
            cantidad_cols_df2 = [col for col in df2.columns if any(x in col.lower() for x in ['cantidad', 'qty', 'stock', 'unidad'])]
            
            if cantidad_cols_df1 and cantidad_cols_df2:
                col_cantidad1 = st.selectbox("Selecciona columna de cantidad en archivo 1:", cantidad_cols_df1)
                col_cantidad2 = st.selectbox("Selecciona columna de cantidad en archivo 2:", cantidad_cols_df2)
                
                # Merge de datos
                df_merge = df1.copy()
                df_merge_temp = df2[[columna2, col_cantidad2]].copy()
                df_merge_temp.columns = [columna2, f"{col_cantidad2}_archivo2"]
                
                df_merge = pd.merge(df_merge, df_merge_temp, left_on=columna1, right_on=columna2, how='left')
                
                # Calcular diferencias
                df_merge['Saldo'] = pd.to_numeric(df_merge[col_cantidad1], errors='coerce') - pd.to_numeric(df_merge[f"{col_cantidad2}_archivo2"], errors='coerce')
                
                st.dataframe(df_merge[[columna1, col_cantidad1, f"{col_cantidad2}_archivo2", 'Saldo', '¿Está en ambos?']], use_container_width=True)
            else:
                st.info("ℹ️ No se detectaron columnas de cantidad en los archivos (búsqueda automática).")

            # Preparar descarga
            archivo_descarga = BytesIO()
            with pd.ExcelWriter(archivo_descarga, engine='xlsxwriter') as writer:
                df1.to_excel(writer, index=False, sheet_name='Comparación')
                if solo_en_1:
                    pd.DataFrame({"Solo en archivo 1": solo_en_1}).to_excel(writer, index=False, sheet_name='Solo Archivo 1')
                if solo_en_2:
                    pd.DataFrame({"Solo en archivo 2": solo_en_2}).to_excel(writer, index=False, sheet_name='Solo Archivo 2')
            archivo_descarga.seek(0)

            st.download_button(
                label="⬇️ Descargar archivo comparado",
                data=archivo_descarga,
                file_name="referencias_comparadas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"⚠️ Ocurrió un error: {e}")
        st.write("Detalles del error:")
        st.code(str(e))