import streamlit as st
import pandas as pd
from io import BytesIO
import re

st.set_page_config(page_title="Comparador de referencias", layout="centered")
st.title("📦 Comparador de referencias entre archivos Excel o CSV")

# Carga de archivos
archivo1 = st.file_uploader("📄 Sube el primer archivo", type=["xlsx", "csv"])
archivo2 = st.file_uploader("📄 Sube el segundo archivo", type=["xlsx", "csv"])

# Columnas de referencia
columna1 = st.text_input("📝 Nombre de la columna referencia en el primer archivo (ej: 'Nota')")
columna2 = st.text_input("📝 Nombre de la columna referencia en el segundo archivo (ej: 'Name')")

# Columnas de cantidad (NUEVAS)
col_cantidad1 = st.text_input("📊 Nombre de la columna cantidad en el primer archivo (ej: 'Codigo')")
col_cantidad2 = st.text_input("📊 Nombre de la columna cantidad en el segundo archivo (ej: 'Producto')")

# Función para leer Excel o CSV
def leer_archivo(archivo):
    if archivo.name.endswith(".csv"):
        return pd.read_csv(archivo)
    else:
        return pd.read_excel(archivo)

# Limpieza personalizada de texto
PALABRAS_PROHIBIDAS = []

def limpiar_referencia(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.upper()
    texto = texto.replace("\n", " ").replace("Ω", "0")
    for palabra in PALABRAS_PROHIBIDAS:
        texto = texto.replace(palabra, "")
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

if archivo1 and archivo2 and columna1 and columna2:
    try:
        df1 = leer_archivo(archivo1)
        df2 = leer_archivo(archivo2)

        if columna1 not in df1.columns:
            st.error(f"❌ La columna '{columna1}' no existe en el primer archivo.")
        elif columna2 not in df2.columns:
            st.error(f"❌ La columna '{columna2}' no existe en el segundo archivo.")
        else:
            df1[columna1] = df1[columna1].apply(limpiar_referencia)
            df2[columna2] = df2[columna2].apply(limpiar_referencia)

            referencias_2 = set(df2[columna2])
            df1["¿Está en ambos?"] = df1[columna1].apply(lambda x: "✅" if x in referencias_2 else "❌")

            st.success("✅ Comparación realizada con éxito.")
            st.subheader("📋 Resultado del primer archivo:")
            st.dataframe(df1)

            # Referencias exclusivas
            refs_1 = set(df1[columna1])
            solo_en_1 = sorted(refs_1 - referencias_2)
            solo_en_2 = sorted(referencias_2 - refs_1)

            with st.expander("🔍 Ver referencias que solo están en el primer archivo"):
                st.write(solo_en_1)

            with st.expander("🔍 Ver referencias que solo están en el segundo archivo"):
                st.write(solo_en_2)

            # --- Comparación de cantidades (MODIFICADO) ---
            if col_cantidad1 and col_cantidad2:  # Verificar que se ingresaron los nombres
                if col_cantidad1 in df1.columns and col_cantidad2 in df2.columns:
                    df_merge = pd.merge(df1, df2[[columna2, col_cantidad2]],
                                        left_on=columna1, right_on=columna2,
                                        how='left')

                    df_merge['¿Cantidad coincide?'] = df_merge.apply(
                        lambda row: '✅' if pd.notnull(row[col_cantidad1]) and pd.notnull(row[col_cantidad2]) and row[col_cantidad1] == row[col_cantidad2] else '❌',
                        axis=1
                    )

                    # Calcular saldo (diferencia)
                    df_merge['Saldo'] = df_merge.apply(
                        lambda row: row[col_cantidad1] - row[col_cantidad2] if pd.notnull(row[col_cantidad1]) and pd.notnull(row[col_cantidad2]) else None,
                        axis=1
                    )

                    st.subheader("📦 Comparación de cantidades:")
                    st.dataframe(df_merge[[columna1, col_cantidad1, col_cantidad2, '¿Cantidad coincide?', 'Saldo']])

                    # Preparar descarga
                    archivo_descarga = BytesIO()
                    with pd.ExcelWriter(archivo_descarga, engine='xlsxwriter') as writer:
                        df_merge.to_excel(writer, index=False, sheet_name='Resultado')
                    archivo_descarga.seek(0)
                else:
                    st.warning(f"⚠️ No se encontraron las columnas '{col_cantidad1}' o '{col_cantidad2}' en los archivos.")
                    archivo_descarga = BytesIO()
                    with pd.ExcelWriter(archivo_descarga, engine='xlsxwriter') as writer:
                        df1.to_excel(writer, index=False, sheet_name='Resultado')
                    archivo_descarga.seek(0)
            else:
                st.info("💡 Ingresa los nombres de las columnas de cantidad para comparar cantidades.")
                archivo_descarga = BytesIO()
                with pd.ExcelWriter(archivo_descarga, engine='xlsxwriter') as writer:
                    df1.to_excel(writer, index=False, sheet_name='Resultado')
                archivo_descarga.seek(0)

            st.download_button(
                label="⬇️ Descargar archivo comparado",
                data=archivo_descarga,
                file_name="referencias_comparadas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"⚠️ Ocurrió un error: {e}")