import streamlit as st
import fitz
import io

st.title("🧠 Editor Inteligente de PDF (con posiciones exactas)")

# Función para detectar campos clave
def detectar_campos(pdf_bytes, campos_busqueda):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    resultados = []

    for num_pagina, page in enumerate(doc):
        texto_pag = page.get_text("dict")
        for bloque in texto_pag["blocks"]:
            for linea in bloque.get("lines", []):
                for span in linea.get("spans", []):
                    texto = span["text"]
                    for campo in campos_busqueda:
                        if campo in texto:
                            resultados.append({
                                "campo": campo,
                                "pagina": num_pagina,
                                "texto": texto,
                                "bbox": span["bbox"],
                                "fuente": span["font"],
                                "tamano": span["size"],
                                "pos_x": span["bbox"][0],
                                "pos_y": span["bbox"][3]
                            })
    doc.close()
    return resultados

# Función para aplicar los cambios en el PDF
def aplicar_ediciones(pdf_bytes, ediciones):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for ed in ediciones:
        page = doc[ed["pagina"]]
        rect = fitz.Rect(*ed["bbox"])
        page.draw_rect(rect, color=(1,1,1), fill=(1,1,1), overlay=True)
        page.insert_text((ed["pos_x"], ed["pos_y"]), ed["nuevo_texto"],
                         fontsize=ed["tamano"], fontname=ed["fuente"], color=(0, 0, 0))
    output = io.BytesIO()
    doc.save(output)
    doc.close()
    return output.getvalue()

# Subida del archivo
uploaded_file = st.file_uploader("📤 Sube un PDF para editar", type=["pdf"])
campos_objetivo = ["SUBTOTAL USD", "GASTOS USD", "TOTAL USD"]

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    st.success("✅ PDF cargado. Buscando campos clave...")

    resultados = detectar_campos(pdf_bytes, campos_objetivo)

    ediciones = []
    for i, res in enumerate(resultados):
        nuevo_texto = st.text_input(f"Editar '{res['campo']}' (Página {res['pagina'] + 1})", value=res["texto"])
        ed = res.copy()
        ed["nuevo_texto"] = nuevo_texto
        ediciones.append(ed)

    if st.button("🛠️ Aplicar Cambios y Descargar"):
        pdf_editado = aplicar_ediciones(pdf_bytes, ediciones)
        st.download_button("⬇️ Descargar PDF Modificado", pdf_editado, "pdf_modificado.pdf", "application/pdf")
