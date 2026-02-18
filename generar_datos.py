import pandas as pd
from datetime import datetime
import os


# ==============================
# CONFIGURACIÓN
# ==============================

DATASET = "datos/subvenciones.csv"


print("Cargando dataset local...")

if not os.path.exists(DATASET):
    print("Dataset no encontrado")
    exit()

df = pd.read_csv(DATASET, sep=";")


# ==============================
# LIMPIEZA
# ==============================

df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
df = df.dropna(subset=["Importe"])


# ==============================
# ANÁLISIS
# ==============================

total_subvenciones = df["Importe"].sum()

top_beneficiarios = (
    df.groupby("Beneficiario")["Importe"]
    .sum()
    .sort_values(ascending=False)
    .head(15)
)

importe_medio = df["Importe"].mean()
max_subvencion = df["Importe"].max()

fecha = datetime.now().strftime("%d/%m/%Y %H:%M")


# ==============================
# GENERAR HTML
# ==============================

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público</title>
<link rel="stylesheet" href="estilo.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>

<header>
<h1>📊 Observatorio Público</h1>
<p>Datos abiertos analizados automáticamente.</p>
<p class="fecha">Actualizado: {fecha}</p>
</header>

<section class="stats">
<div class="card big">
Total subvenciones:<br>
<b>{total_subvenciones:,.0f} €</b>
</div>

<div class="card">
Media subvención:<br>
<b>{importe_medio:,.0f} €</b>
</div>

<div class="card">
Mayor subvención:<br>
<b>{max_subvencion:,.0f} €</b>
</div>
</section>

<section>
<h2>Top beneficiarios</h2>
"""

for nombre, importe in top_beneficiarios.items():
    html += f"""
    <div class="card">
        <b>{nombre}</b>
        <span>{importe:,.0f} €</span>
    </div>
    """

html += """
</section>

<footer>
Proyecto ciudadano · Datos públicos abiertos
</footer>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Web generada correctamente")
