import cadquery as cq

# Parámetros del diseño
canal_principal_diam = 6.0  # mm
canal_secundario_diam = 4.5  # mm
distancia_entre_cavidades = 30.0  # mm
altura_canal = 3.0  # Altura de extrusión

# Crear el path del canal principal (horizontal)
trayectoria_principal = (
    cq.Workplane("XY")
    .moveTo(-distancia_entre_cavidades / 2, 0)
    .lineTo(distancia_entre_cavidades / 2, 0)
)

# Crear el canal principal
canal_principal = (
    cq.Workplane("XZ")
    .center(0, 0)
    .circle(canal_principal_diam / 2)
    .sweep(trayectoria_principal, isFrenet=True)
)

# Función para crear canales secundarios verticales
def crear_canal_vertical(x, direccion):
    path = (
        cq.Workplane("XY")
        .moveTo(x, 0)
        .lineTo(x, direccion * distancia_entre_cavidades / 2)
    )
    return (
        cq.Workplane("XZ")
        .center(0, 0)
        .circle(canal_secundario_diam / 2)
        .sweep(path, isFrenet=True)
    )

# Unir todos los canales
canal_total = canal_principal
for x in [-distancia_entre_cavidades / 2, distancia_entre_cavidades / 2]:
    canal_total = canal_total.union(crear_canal_vertical(x, 1))  # arriba
    canal_total = canal_total.union(crear_canal_vertical(x, -1))  # abajo

# Exportar a STEP
cq.exporters.export(canal_total, "canal_inyeccion_balanceado.step")
