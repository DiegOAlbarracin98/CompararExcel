import pandas as pd

# === 1️⃣ CONFIGURACIÓN BÁSICA ===
excel_path = "precios-productos.xlsx"  # Cambia la ruta si el archivo no está en la misma carpeta
table_name = "productos"

# === 2️⃣ LEER EL ARCHIVO EXCEL ===
df = pd.read_excel(excel_path)

# === 3️⃣ DEFINIR ESTRUCTURA DE LA TABLA ===
columns_def = {"id_cartera": "INT NOT NULL AUTO_INCREMENT PRIMARY KEY"}
for col in df.columns:
    columns_def[col] = "VARCHAR(255)"  # Puedes ajustar el tipo de dato aquí

# Crear sentencia CREATE TABLE
create_stmt = f"CREATE TABLE `{table_name}` (\n"
create_stmt += ",\n".join([f"  `{col}` {dtype}" for col, dtype in columns_def.items()])
create_stmt += "\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;\n"

# === 4️⃣ GENERAR INSERTS ===
insert_statements = []
col_list_sql = "`, `".join(df.columns)

for _, row in df.iterrows():
    values = []
    for v in row:
        if pd.isna(v):
            values.append("NULL")
        else:
            s = str(v).replace("'", "''")  # Escapar comillas simples
            values.append(f"'{s}'")
    values_sql = ", ".join(values)
    insert_statements.append(f"INSERT INTO `{table_name}` (`{col_list_sql}`) VALUES ({values_sql});")

# === 5️⃣ GUARDAR LOS ARCHIVOS SQL ===

# Estructura + datos
with open("cartera_clientes_estructura_y_datos.sql", "w", encoding="utf-8") as f:
    f.write(create_stmt + "\n" + "\n".join(insert_statements))

print("✅ Archivos SQL generados correctamente:")
print(" - cartera_clientes_estructura.sql")
print(" - cartera_clientes_estructura_y_datos.sql")
