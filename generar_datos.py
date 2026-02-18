import pandas as pd
import requests
from datetime import datetime

# ===============================
# DATASET OFICIAL SUBVENCIONES
# ===============================

URL_DATOS = "https://www.infosubvenciones.es/bdnstrans/GE/es/concesiones.csv"

print("Descargando dataset oficial...")

try:
    df = pd.read_csv(URL_DATOS, sep=";", encoding="latin1", low_memory=False)
except Exception as e:
    print("Error dataset:", e)
    df = pd.DataFrame()

# ===============================
# LIMPIEZA
# ===============================

if not df.empty and "Importe" in df.columns:

    df["Importe"] = pd.to_numeric(df["Importe"], errors="coerce")
    df = df.dropna(subset=["Importe"])

    total = df["Importe"].sum()
    media = df["Importe"].mean()
    mayor = df["Importe"].max()

    top = (
        df.groupby("Beneficiario")["Importe"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

else:
    total = media = mayor = 0
    top = {}

# ===============================
# INSIGHT AUTOMÁTICO
# ===============================

if total > 1_000_000_000:
    insight = "Nivel muy alto de gasto público en subvenciones."
elif total > 100_000_000:
    insight = "Volumen relevante de ayudas públicas."
else:
    insight = "Nivel moderado de subvenciones."

# ===============================
# FECHA
# ===============================

fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

# ===============================
# HTML GENERADO
# ===============================

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Observatorio Público</title>

<link rel="stylesheet" href="estilo.css">
<meta name="viewport" content="width=device-width, initial-scale=1">

<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">

</head>

<body>

<header>
<h1>📊 Observatorio Público</h1>
<p>Datos abiertos analizados automáticamente.</p>
<p class="fecha">Actualizado: {fecha}</p>
</header>

<section class="stats">
<h2>Total subvenciones</h2>
<p class="big">{total:,.0f} €</p>

<div class="grid">
<div>Media: {media:,.0f} €</div>
<div>Mayor: {mayor:,.0f} €</div>
</div>
</section>

<section>
<h2>Insight automático</h2>
<p>{insight}</p>
</section>

<section>
<h2>Top beneficiarios</h2>
"""

for nombre, importe in top.items():
    html += f"<div class='card'><b>{nombre}</b> — {importe:,.0f} €</div>"

html += """

</section>

<footer>
Proyecto ciudadano · Datos públicos oficiales
</footer>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Web generada correctamente")
